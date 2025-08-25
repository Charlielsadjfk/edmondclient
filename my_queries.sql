//List all users and the amount of posts they have
SELECT u.userID, u.name, u.email, COUNT(p.postID) AS total_posts
FROM USER u
LEFT JOIN post p ON u.userID = p.userID
GROUP BY u.userID, u.name, u.email
ORDER BY total_posts DESC;

//Find the 10 most recent posts with user names
SELECT p.postID, u.name, p.title, p.content, p.postdate
FROM post p
JOIN USER u ON p.userID = u.userID
ORDER BY p.postdate DESC
LIMIT 10;

//average rating per user
SELECT u.userID, u.name, AVG(p.rating) AS avg_rating
FROM USER u
JOIN post p ON u.userID = p.userID
GROUP BY u.userID, u.name
ORDER BY avg_rating DESC;

//Posts containing a specific keyword (e.g., "Hello")
SELECT p.postID, u.name, p.title, p.content, p.postdate
FROM post p
JOIN USER u ON p.userID = u.userID
WHERE p.content LIKE '%Loved this!%'
ORDER BY p.postdate DESC;

//Users who never posted anything
SELECT u.userID, u.name, u.email
FROM USER u
LEFT JOIN post p ON u.userID = p.userID
WHERE p.postID IS NULL;
