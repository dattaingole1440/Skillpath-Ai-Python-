import sqlite3
conn = sqlite3.connect('skillpath_ai.db')
c = conn.cursor()
c.execute("SELECT id, name, email, role FROM users WHERE role IN ('college_admin', 'principal', 'hod', 'super_admin', 'admin')")
for r in c.fetchall():
    print(r)
print("---all roles---")
c.execute("SELECT DISTINCT role FROM users")
for r in c.fetchall():
    print(r)
conn.close()
