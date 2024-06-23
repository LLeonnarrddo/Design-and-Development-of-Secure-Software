-- 
-- 
--    =========================================
--    Design and Development of Secure Software
--    ============= MSI 2019/2020 =============
--    ======== Practical Assignment #2 ========
--    =========================================
--
--      Department of Informatics Engineering
--              University of Coimbra          
--   
--          Nuno Antunes <nmsa@dei.uc.pt>
--          João Antunes <jcfa@dei.uc.pt>
--          Marco Vieira <mvieira@dei.uc.pt>
-- 
-- 
/* 
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS books;
*/
CREATE TABLE users (
    username    VARCHAR( 32)    primary key,
    password    VARCHAR(512)    NOT NULL,
    secret_key  VARCHAR(64)     NOT NULL
);

CREATE TABLE users_vulnerable (
    username    VARCHAR( 32)    primary key,
    password    VARCHAR(512)    NOT NULL
);


CREATE TABLE messages (
    message_id  SERIAL PRIMARY KEY,
    author      VARCHAR( 16)   ,
    message     VARCHAR(256)    NOT NULL
);

CREATE TABLE books (
    book_id         SERIAL PRIMARY KEY,
    title           VARCHAR(128),
    authors         VARCHAR(256),
    category        VARCHAR(128),
    price           NUMERIC(8,2),
    book_date       DATE,
    description     VARCHAR(1024),
    keywords        VARCHAR(256),
    notes           VARCHAR(256),
    recomendation   INTEGER
);



-- Default data for messages
insert into messages (author, message)
          values ('Vulnerable', 'Hi! I wrote this message using Vulnerable Form.');

insert into messages (author, message)
          values ('Correct', 'OMG! This form is so correct!!!');

insert into messages (author, message)
          values ('Vulnerable', 'Oh really?');





-- Default data for books

insert into books (title, authors, category, price, book_date, keywords, notes, recomendation,
                   description)
       values('Web Database Development : Step by Step', 'Jim Buyens', 'Databases',  39.99, '2007-01-01 12:00:00', 'Web; persistence; sql', 'This is a very nice book.', 10,
            'As Web sites continue to grow in complexity and in the volume of data they must present, databases increasingly drive their content. WEB DATABASE DEVELOPMENT FUNDAMENTALS is ideal for the beginning-to-intermediate Web developer, departmental power user, or entrepreneur who wants to step up to a database-driven Web site-without buying several in-depth guides to the different technologies involved. This book uses the clear Microsoft(r) Step by Step tutorial method to familiarize developers with the technologies for building smart Web sites that present data more easily. ');


insert into books (title, authors, category, price, book_date, keywords, notes, recomendation,
                   description)
       values('Programming Perl (3rd Edition)', 'Larry Wall, Tom Christiansen, Jon Orwant', 'Programming',  39.96, '2009-12-01 12:00:00', 'Perrl; scripts; code', 'This is a very nice book.', 9, 
            'Perl is a powerful programming language that has grown in popularity since it first appeared in 1988. The first edition of this book, Programming Perl, hit the shelves in 1990, and was quickly adopted as the undisputed bible of the language. Since then, Perl has grown with the times, and so has this book.
Programming Perl is not just a book about Perl. It is also a unique introduction to the language and its culture, as you might expect only from its authors. Larry Wall is the inventor of Perl, and provides a unique perspective on the evolution of Perl and its future direction. Tom Christiansen was one of the first champions of the language, and lives and breathes the complexities of Perl internals as few other mortals do. Jon Orwant is the editor of The Perl Journal, which has brought together the Perl community as a common forum for new developments in Perl.');


insert into books (title, authors, category, price, book_date, keywords, notes, recomendation,
                   description)
       values('Perl and CGI for the World Wide Web: Visual QuickStart Guide', 'Elizabeth Castro', 'Programming',  15.19, '2009-06-01 12:00:00', 'Perral; scripts; code', 'This is a very nice book.', 18, 
            'Taking a visual approach, this guide uses ample screen stills to explain the basic components of Perl, and show how to install and customize existing CGI scripts to build interactivity into Web sites.');


insert into books (title, authors, category, price, book_date, keywords, notes, recomendation,
                   description)
       values('Teach Yourself ColdFusion in 21 Days (Teach Yourself -- 21 Days)', 'Charles Mohnike', 'HTML & Web design',  31.99, '2009-06-01 12:00:00', 'Client; scripts; code', 'This is a meager book.', 1, 
            'Sams Teach Yourself ColdFusion in 21 Days quickly empowers you to create your own dynamic database-driven Web applications using Allaire''s ColdFusion. Using client-proven methods, and the success of his popular ColdFusion tutorial for Wired, expert author Charles Mohnike provides you with an understanding of the ColdFusion Server and guides you through the use of the ColdFusion Studio, enabling you to create your own ColdFusion applications quickly and easily. Topics such as installing and configuring the ColdFusion Server, working with the ColdFusion Studio, working with SQL, optimizing your datasource, understanding templates and ColdFusion Markup Language (CFML), using ColdFusion tags, manipulating data, creating e-commerce solutions with ColdFusion, and debugging ColdFusion applications.');



insert into books (title, authors, category, price, book_date, keywords, notes, recomendation,
                   description)
       values('ColdFusion Fast & Easy Web Development', 'T. C., III Bradley', 'HTML & Web design',  31.99, '2009-06-01 12:00:00', 'Cold; scripts; code', 'This is a meager book.', 1, 
            'Allaires ColdFusion is a powerful solution for developers wanting to build secure, scalable, and manageable Web applications. ColdFusion Fast & Easy Web Development takes a visual approach to learning this Web application server. It combines easy-to-understand instructions and real screen shots for a truly unique learning experience. This book covers topics from ColdFusion basics to retrieving data to building dynamic queries and applications with ColdFusion. The innovative, visual approach of the Fast & Easy Web Development series provides a perfect format for programmers of all levels.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('Learn Python in 30 Days', 'Alice Johnson', 'Programming', 34.99, '2022-05-10 11:00:00', 'Python; programming; beginners', 'A month-long guide to mastering Python.', 9,
    'This book is designed for beginners who want to learn Python quickly. Each chapter provides hands-on exercises and practical examples to reinforce your programming skills.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('JavaScript Mastery: Modern Web Development', 'Brian Adams', 'Programming', 44.99, '2022-04-18 14:15:00', 'JavaScript; web development; frontend', 'Unlock the full potential of JavaScript.', 8,
    'Explore advanced JavaScript concepts and modern web development techniques. This book is ideal for developers looking to enhance their skills in building dynamic and responsive web applications.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('SQL Fundamentals: Database Querying', 'Jennifer Lee', 'Databases', 39.99, '2022-03-25 12:30:00', 'SQL; database querying; fundamentals', 'A comprehensive guide to SQL and database querying.', 10,
    'Master the art of SQL and database querying with this detailed guide. It covers everything from basic SELECT statements to complex JOIN operations.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('NoSQL Databases: Beyond Relational Data', 'Michael Turner', 'Databases', 49.99, '2023-02-12 10:45:00', 'NoSQL; non-relational databases; data modeling', 'Explore the world of non-relational databases.', 9,
    'Delve into NoSQL databases and understand how they handle non-relational data. This book provides insights into various NoSQL models and their practical applications.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('HTML5 and CSS3: Building Responsive Websites', 'Karen Davis', 'HTML & Web design', 29.99, '2023-01-08 15:00:00', 'HTML5; CSS3; responsive design', 'Create modern and responsive websites.', 8,
    'Learn the latest techniques in HTML5 and CSS3 to build visually appealing and responsive websites. This book is suitable for both beginners and experienced web developers.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('UX Design: Creating Exceptional User Experiences', 'Charles Mohnike', 'HTML & Web design', 54.99, '2023-12-18 13:45:00', 'UX design; user experience; web design', 'Design websites with a focus on user experience.', 10,
    'Master the principles of UX design and create websites that provide exceptional user experiences. This book covers usability, accessibility, and best practices in web design.');



INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('Java Programming: Advanced Concepts', 'Tom Christiansen', 'Programming', 49.99, '2023-12-10 14:30:00', 'Java; programming; advanced', 'Deepen your understanding of Java programming.', 9,
    'Explore advanced concepts in Java programming, including multithreading, design patterns, and advanced data structures.');


INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('MongoDB Essentials: Practical NoSQL', 'Jim Buyens', 'Databases', 44.99, '2023-08-20 11:15:00', 'MongoDB; NoSQL; database essentials', 'Practical guide to MongoDB for NoSQL enthusiasts.', 8,
    'Learn the essentials of MongoDB and NoSQL database management. This book provides hands-on examples and real-world scenarios for effective MongoDB implementation.');


INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('Responsive Web Design with Bootstrap', 'Christopher King', 'HTML & Web design', 39.99, '2023-11-28 10:00:00', 'Bootstrap; responsive design; web development', 'Create responsive web pages with Bootstrap.', 9,
    'Master the art of responsive web design using the popular Bootstrap framework. This book includes practical examples and tips for building visually appealing and user-friendly websites.');


INSERT INTO books (title, authors, category, price, book_date, keywords, notes, recomendation, description)
VALUES
    ('C# Programming: Object-Oriented Mastery', 'Larry Wall', 'Programming', 54.99, '2023-10-26 12:45:00', 'C#; object-oriented programming; mastery', 'Become an expert in object-oriented programming with C#.', 10,
    'This book focuses on mastering object-oriented programming concepts using the C# language. It covers inheritance, polymorphism, and encapsulation in-depth.');

