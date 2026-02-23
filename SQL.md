## SQL Answers

1) Get all statuses, not repeating, alphabetically ordered
```sql
SELECT DISTINCT status
FROM tasks
ORDER BY status ASC;
```

2) Get the count of all tasks in each project, order by tasks count descending
```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
GROUP BY p.id, p.name
ORDER BY task_count DESC;
```

3) Get the count of all tasks in each project, order by projects names
```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
GROUP BY p.id, p.name
ORDER BY p.name ASC;
```

4) Get the tasks for all projects having the name beginning with "N" letter
```sql
SELECT t.*
FROM tasks AS t
JOIN projects AS p ON p.id = t.project_id
WHERE p.name LIKE 'N%';
```

5) Get the list of all projects containing the 'a' letter in the middle of the name,
   and show the tasks count near each project. Mention that there can exist projects
   without tasks and tasks with project_id = NULL.
```sql
SELECT p.id, p.name, COUNT(t.id) AS task_count
FROM projects AS p
LEFT JOIN tasks AS t ON t.project_id = p.id
WHERE p.name LIKE '%a%'
GROUP BY p.id, p.name
ORDER BY p.name ASC;
```

6) Get the list of tasks with duplicate names. Order alphabetically
```sql
SELECT t.name, COUNT(*) AS duplicate_count
FROM tasks AS t
GROUP BY t.name
HAVING COUNT(*) > 1
ORDER BY t.name ASC;
```

7) Get the list of tasks having several exact matches of both name and status,
   from the project 'Delivery’. Order by matches count
```sql
SELECT t.name, t.status, COUNT(*) AS match_count
FROM tasks AS t
JOIN projects AS p ON p.id = t.project_id
WHERE p.name = 'Delivery'
GROUP BY t.name, t.status
HAVING COUNT(*) > 1
ORDER BY match_count DESC;
```

8) Get the list of project names having more than 10 tasks in status 'completed'.
   Order by project_id
```sql
SELECT p.id, p.name
FROM projects AS p
JOIN tasks AS t ON t.project_id = p.id
WHERE t.status = 'completed'
GROUP BY p.id, p.name
HAVING COUNT(*) > 10
ORDER BY p.id ASC;
```
