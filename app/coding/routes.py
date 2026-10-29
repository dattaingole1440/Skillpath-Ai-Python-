import json
import sys
import io
import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import User, Topic, StudentProgress, CodingChallenge, CodingSubmission, QuizAttempt, Quiz, ActivityLog, Analytics, Roadmap, Career
from app.utils.auth import get_current_user
from app.schemas import schemas

router = APIRouter(prefix="/coding", tags=["Coding Challenge"])
templates = Jinja2Templates(directory="app/templates")

def execute_python_code(code: str, test_cases_json: str) -> tuple[str, int, list]:
    """
    Safely executes user Python code against test cases in an isolated local dictionary scope.
    Captures output (stdout) and checks results.
    Returns (status, score_earned, test_results)
    """
    # Parse test cases
    try:
        test_cases = json.loads(test_cases_json) if test_cases_json else []
    except Exception:
        test_cases = []

    test_results = []
    passed_count = 0
    total_tests = len(test_cases)
    
    # Setup standard stdout redirect
    old_stdout = sys.stdout
    
    # Execute code in a fresh global dict
    local_scope = {}
    
    try:
        # Compile user code
        compiled_code = compile(code, "<student_code>", "exec")
        
        # Execute code redirecting stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        exec(compiled_code, {}, local_scope)
        sys.stdout = old_stdout
        
        stdout_content = redirected_output.getvalue()
        
    except SyntaxError as se:
        sys.stdout = old_stdout
        return "failed", 0, [{"name": "Compilation", "passed": False, "message": f"Syntax Error: {se.msg} on line {se.lineno}"}]
    except Exception as e:
        sys.stdout = old_stdout
        return "failed", 0, [{"name": "Execution", "passed": False, "message": f"Runtime Error: {str(e)}"}]

    # Run tests if compilation succeeded
    for idx, tc in enumerate(test_cases):
        func_name = tc.get("function_name", "")
        args = tc.get("args", [])
        expected = tc.get("expected", None)
        test_name = f"Test Case {idx + 1} ({func_name})"
        
        if func_name not in local_scope:
            test_results.append({
                "name": test_name,
                "passed": False,
                "message": f"Function '{func_name}' not found in submission. Please check your function name."
            })
            continue

        try:
            # Call target function
            target_func = local_scope[func_name]
            # Run redirecting stdout for print captures inside function
            func_stdout = io.StringIO()
            sys.stdout = func_stdout
            result = target_func(*args)
            sys.stdout = old_stdout
            
            # Simple equal check (cast expected dynamically based on type)
            # Handle float epsilon checks or string exact match
            if isinstance(result, str):
                is_correct = (result.strip() == str(expected).strip())
            else:
                is_correct = (result == expected)

            if is_correct:
                passed_count += 1
                test_results.append({
                    "name": test_name,
                    "passed": True,
                    "message": f"Inputs: {args} -> Output: {result}. Match successful."
                })
            else:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Inputs: {args} -> Expected: {expected}, but got: {result}."
                })
        except Exception as e:
            sys.stdout = old_stdout
            test_results.append({
                "name": test_name,
                "passed": False,
                "message": f"Failed with error: {str(e)}"
            })

    # Determine overall status
    status_str = "passed" if (total_tests == 0 or passed_count == total_tests) else "failed"
    score = 100 if status_str == "passed" else int((passed_count / total_tests * 100) if total_tests > 0 else 0)

    return status_str, score, test_results


def execute_java_code(code: str, test_cases_json: str) -> tuple[str, int, list]:
    """
    Compiles and executes student Java code against test cases.
    """
    try:
        test_cases = json.loads(test_cases_json) if test_cases_json else []
    except Exception:
        test_cases = []

    test_results = []
    passed_count = 0
    total_tests = len(test_cases)
    
    if total_tests == 0:
        return "passed", 100, []

    import tempfile
    import subprocess
    import shutil
    import os

    temp_dir = tempfile.mkdtemp(prefix="java_run_")
    
    try:
        solution_path = os.path.join(temp_dir, "Solution.java")
        with open(solution_path, "w", encoding="utf-8") as f:
            f.write(code)

        def format_java_arg(arg):
            if isinstance(arg, bool):
                return "true" if arg else "false"
            elif isinstance(arg, str):
                return f'"{arg}"'
            elif isinstance(arg, list):
                elements = ", ".join(str(x) for x in arg)
                return f"new int[]{{{elements}}}"
            else:
                return str(arg)

        runner_code = [
            "public class TestRunner {",
            "    public static void main(String[] args) {",
            "        try {"
        ]
        
        for idx, tc in enumerate(test_cases):
            func_name = tc.get("function_name", "")
            args = tc.get("args", [])
            formatted_args = ", ".join(format_java_arg(x) for x in args)
            runner_code.append(f'            try {{')
            runner_code.append(f'                System.out.println("TC_RESULT_{idx}:" + Solution.{func_name}({formatted_args}));')
            runner_code.append(f'            }} catch (Exception e) {{')
            runner_code.append(f'                System.out.println("TC_RESULT_{idx}:ERROR:" + e.getMessage());')
            runner_code.append(f'            }}')
            
        runner_code.extend([
            "        } catch (Exception e) {",
            "            System.out.println(\"ERROR:\" + e.getMessage());",
            "        }",
            "    }",
            "}"
        ])

        runner_path = os.path.join(temp_dir, "TestRunner.java")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write("\n".join(runner_code))

        compile_proc = subprocess.run(
            ["javac", "Solution.java", "TestRunner.java"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if compile_proc.returncode != 0:
            err_msg = compile_proc.stderr or compile_proc.stdout
            return "failed", 0, [{"name": "Compilation", "passed": False, "message": f"Compilation Error: {err_msg}"}]

        run_proc = subprocess.run(
            ["java", "TestRunner"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        run_output = run_proc.stdout
        run_err = run_proc.stderr

        outputs_map = {}
        for line in run_output.splitlines():
            if line.startswith("TC_RESULT_"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    outputs_map[parts[0]] = parts[1]

        for idx, tc in enumerate(test_cases):
            func_name = tc.get("function_name", "")
            args = tc.get("args", [])
            expected = tc.get("expected", None)
            test_name = f"Test Case {idx + 1} ({func_name})"
            
            key = f"TC_RESULT_{idx}"
            if key not in outputs_map:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Execution failed. Expected result output not captured. Error: {run_err}"
                })
                continue
                
            actual_val = outputs_map[key]
            
            if actual_val.startswith("ERROR"):
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Runtime Exception: {actual_val}"
                })
                continue

            is_correct = False
            if isinstance(expected, bool):
                is_correct = (actual_val.lower() == str(expected).lower())
            elif isinstance(expected, (int, float)):
                try:
                    is_correct = (abs(float(actual_val) - float(expected)) < 1e-5)
                except ValueError:
                    is_correct = (actual_val == str(expected))
            else:
                is_correct = (actual_val.strip() == str(expected).strip())

            if is_correct:
                passed_count += 1
                test_results.append({
                    "name": test_name,
                    "passed": True,
                    "message": f"Inputs: {args} -> Output: {actual_val}. Match successful."
                })
            else:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Inputs: {args} -> Expected: {expected}, but got: {actual_val}."
                })

    except subprocess.TimeoutExpired:
        return "failed", 0, [{"name": "Execution", "passed": False, "message": "Execution Timeout (Infinite Loop suspected)"}]
    except Exception as e:
        return "failed", 0, [{"name": "Execution", "passed": False, "message": f"System execution error: {str(e)}"}]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    status_str = "passed" if (passed_count == total_tests) else "failed"
    score = 100 if status_str == "passed" else int((passed_count / total_tests * 100) if total_tests > 0 else 0)
    return status_str, score, test_results


def execute_cpp_code(code: str, test_cases_json: str) -> tuple[str, int, list]:
    """
    Compiles and executes student C++ code against test cases.
    """
    try:
        test_cases = json.loads(test_cases_json) if test_cases_json else []
    except Exception:
        test_cases = []

    test_results = []
    passed_count = 0
    total_tests = len(test_cases)
    
    if total_tests == 0:
        return "passed", 100, []

    import tempfile
    import subprocess
    import shutil
    import os

    temp_dir = tempfile.mkdtemp(prefix="cpp_run_")
    
    try:
        def format_cpp_arg(arg):
            if isinstance(arg, bool):
                return "true" if arg else "false"
            elif isinstance(arg, str):
                return f'"{arg}"'
            elif isinstance(arg, list):
                elements = ", ".join(str(x) for x in arg)
                return f"std::vector<int>{{{elements}}}"
            else:
                return str(arg)

        runner_code = [
            "#include <iostream>",
            "#include <string>",
            "#include <vector>",
            "#include <map>",
            "#include <algorithm>",
            "",
            code,
            "",
            "int main() {",
            "    try {"
        ]

        for idx, tc in enumerate(test_cases):
            func_name = tc.get("function_name", "")
            args = tc.get("args", [])
            
            if func_name == "double_val":
                runner_code.append(f"        int val_{idx} = {args[0]};")
                runner_code.append(f"        std::cout << \"TC_RESULT_{idx}:\" << {func_name}(&val_{idx}) << std::endl;")
            else:
                formatted_args = ", ".join(format_cpp_arg(x) for x in args)
                runner_code.append(f"        std::cout << \"TC_RESULT_{idx}:\" << {func_name}({formatted_args}) << std::endl;")
            
        runner_code.extend([
            "    } catch (...) {",
            "        std::cout << \"ERROR: Exception thrown\" << std::endl;",
            "    }",
            "    return 0;",
            "}"
        ])

        runner_path = os.path.join(temp_dir, "runner.cpp")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write("\n".join(runner_code))

        exe_name = "runner.exe" if os.name == "nt" else "runner"
        compile_proc = subprocess.run(
            ["g++", "-o", exe_name, "runner.cpp"],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if compile_proc.returncode != 0:
            err_msg = compile_proc.stderr or compile_proc.stdout
            return "failed", 0, [{"name": "Compilation", "passed": False, "message": f"Compilation Error: {err_msg}"}]

        run_proc = subprocess.run(
            [os.path.join(temp_dir, exe_name)],
            cwd=temp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        run_output = run_proc.stdout
        run_err = run_proc.stderr

        outputs_map = {}
        for line in run_output.splitlines():
            if line.startswith("TC_RESULT_"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    outputs_map[parts[0]] = parts[1]

        for idx, tc in enumerate(test_cases):
            func_name = tc.get("function_name", "")
            args = tc.get("args", [])
            expected = tc.get("expected", None)
            test_name = f"Test Case {idx + 1} ({func_name})"
            
            key = f"TC_RESULT_{idx}"
            if key not in outputs_map:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Execution failed. Expected result output not captured. Error: {run_err}"
                })
                continue
                
            actual_val = outputs_map[key]
            
            if "ERROR" in actual_val:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Runtime Exception: {actual_val}"
                })
                continue

            is_correct = False
            if isinstance(expected, bool):
                is_correct = (actual_val == "1" if expected else actual_val == "0")
            elif isinstance(expected, (int, float)):
                try:
                    is_correct = (abs(float(actual_val) - float(expected)) < 1e-5)
                except ValueError:
                    is_correct = (actual_val == str(expected))
            else:
                is_correct = (actual_val.strip() == str(expected).strip())

            if is_correct:
                passed_count += 1
                test_results.append({
                    "name": test_name,
                    "passed": True,
                    "message": f"Inputs: {args} -> Output: {actual_val}. Match successful."
                })
            else:
                test_results.append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Inputs: {args} -> Expected: {expected}, but got: {actual_val}."
                })

    except subprocess.TimeoutExpired:
        return "failed", 0, [{"name": "Execution", "passed": False, "message": "Execution Timeout (Infinite Loop suspected)"}]
    except Exception as e:
        return "failed", 0, [{"name": "Execution", "passed": False, "message": f"System execution error: {str(e)}"}]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    status_str = "passed" if (passed_count == total_tests) else "failed"
    score = 100 if status_str == "passed" else int((passed_count / total_tests * 100) if total_tests > 0 else 0)
    return status_str, score, test_results


@router.get("/challenge/{challenge_id}", response_class=HTMLResponse)
def get_challenge(challenge_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
        
    topic = db.query(Topic).filter(Topic.id == challenge.topic_id).first()
    
    # Check if topic is unlocked
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == current_user.id,
        StudentProgress.topic_id == topic.id
    ).first()
    
    if (not progress or progress.status == "Locked") and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="This challenge is locked. Unlock the topic first.")

    # Get previous submissions
    submissions = db.query(CodingSubmission).filter(
        CodingSubmission.student_id == current_user.id,
        CodingSubmission.challenge_id == challenge_id
    ).order_by(CodingSubmission.submitted_at.desc()).all()

    return templates.TemplateResponse(
        "coding/challenge.html",
        {
            "request": request,
            "user": current_user,
            "challenge": challenge,
            "topic": topic,
            "submissions": submissions
        }
    )


@router.post("/submit/{challenge_id}", response_model=schemas.CodeResultResponse)
def submit_challenge(
    challenge_id: int,
    submission: schemas.CodeSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(CodingChallenge).filter(CodingChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Determine career track for compilation type
    topic = db.query(Topic).filter(Topic.id == challenge.topic_id).first()
    roadmap = db.query(Roadmap).filter(Roadmap.id == topic.roadmap_id).first() if topic else None
    career = db.query(Career).filter(Career.id == roadmap.career_id).first() if roadmap else None

    # Run code execution engine based on active skill / career
    if career and career.name == "Java Developer":
        status_str, score, test_results = execute_java_code(
            submission.submitted_code,
            challenge.test_cases
        )
    elif career and career.name == "C++ Developer":
        status_str, score, test_results = execute_cpp_code(
            submission.submitted_code,
            challenge.test_cases
        )
    else:
        status_str, score, test_results = execute_python_code(
            submission.submitted_code,
            challenge.test_cases
        )

    # 1. Save coding submission
    code_sub = CodingSubmission(
        student_id=current_user.id,
        challenge_id=challenge.id,
        submitted_code=submission.submitted_code,
        status=status_str,
        score_earned=score
    )
    db.add(code_sub)
    db.commit()
    db.refresh(code_sub)

    # 2. Recalculate Student Coding Average
    all_subs = db.query(CodingSubmission).filter(CodingSubmission.student_id == current_user.id).all()
    if all_subs:
        current_user.coding_avg = round(sum(sub.score_earned for sub in all_subs) / len(all_subs), 1)

    # 3. Log Activity and Analytics
    log = ActivityLog(
        user_id=current_user.id,
        action="submit_code",
        details=f"Submitted coding challenge '{challenge.title}' with score {score}% ({status_str})."
    )
    db.add(log)
    
    today = datetime.date.today()
    analytic_rec = db.query(Analytics).filter(
        Analytics.student_id == current_user.id,
        Analytics.date == today
    ).first()
    if not analytic_rec:
        analytic_rec = Analytics(student_id=current_user.id, date=today, coding_score=score)
        db.add(analytic_rec)
    else:
        analytic_rec.coding_score = score
        
    db.commit()

    # 4. Check adaptation progression: Mark topic completed and unlock next topic if both quiz and coding passed
    # Check if quiz is passed
    quiz = db.query(Quiz).filter(Quiz.topic_id == challenge.topic_id).first()
    quiz_passed = True
    if quiz:
        best_quiz = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == current_user.id,
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.passed == True
        ).first()
        quiz_passed = best_quiz is not None

    # Check if ALL other challenges for this topic are passed
    all_challenges = db.query(CodingChallenge).filter(CodingChallenge.topic_id == challenge.topic_id).all()
    all_challenges_passed = True
    for chal in all_challenges:
        best_sub = db.query(CodingSubmission).filter(
            CodingSubmission.student_id == current_user.id,
            CodingSubmission.challenge_id == chal.id,
            CodingSubmission.status == "passed"
        ).first()
        if not best_sub and chal.id != challenge_id:
            all_challenges_passed = False
            break
            
    # Include current submission status
    if status_str != "passed":
        all_challenges_passed = False

    if quiz_passed and all_challenges_passed:
        # Mark current topic as Completed
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == current_user.id,
            StudentProgress.topic_id == challenge.topic_id
        ).first()
        if progress:
            if progress.status != "Completed":
                progress.status = "Completed"
                progress.completed_at = datetime.datetime.utcnow()
                if analytic_rec:
                    analytic_rec.topics_completed += 1
                db.commit()

            # Unlock the next topic in the roadmap
            current_topic = db.query(Topic).filter(Topic.id == challenge.topic_id).first()
            if current_topic:
                roadmap_topics = db.query(Topic).filter(
                    Topic.roadmap_id == current_topic.roadmap_id
                ).order_by(Topic.order).all()
                
                # Check within current roadmap
                next_t = None
                for idx, t in enumerate(roadmap_topics):
                    if t.id == current_topic.id and idx + 1 < len(roadmap_topics):
                        next_t = roadmap_topics[idx + 1]
                        break
                
                # If not found in current roadmap, check subsequent roadmap order
                if not next_t:
                    current_roadmap = db.query(Roadmap).filter(Roadmap.id == current_topic.roadmap_id).first()
                    next_roadmap = db.query(Roadmap).filter(
                        Roadmap.career_id == current_user.current_career_id,
                        Roadmap.order > current_roadmap.order
                    ).order_by(Roadmap.order).first()
                    if next_roadmap:
                        next_t = db.query(Topic).filter(Topic.roadmap_id == next_roadmap.id).order_by(Topic.order).first()
                
                if next_t:
                    next_progress = db.query(StudentProgress).filter(
                        StudentProgress.student_id == current_user.id,
                        StudentProgress.topic_id == next_t.id
                    ).first()
                    if not next_progress:
                        next_progress = StudentProgress(
                            student_id=current_user.id,
                            topic_id=next_t.id,
                            status="Unlocked"
                        )
                        db.add(next_progress)
                    elif next_progress.status == "Locked":
                        next_progress.status = "Unlocked"
                    db.commit()

    total_tests = len(test_results)
    passed_count = sum(1 for r in test_results if r.get("passed", False))

    return {
        "status": status_str,
        "output": f"Tests executed. Passed {passed_count}/{total_tests} tests.",
        "score_earned": score,
        "test_results": test_results
    }
