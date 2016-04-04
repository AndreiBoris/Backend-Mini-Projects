rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

### Files and commands we’ll be using (Relational Databases)

Files installed for this class are located in the `/vagrant` directory inside the virtual machine. Everything here is automatically shared with the `vagrant` directory inside the `vm` directory on your computer. Any code files you save into that directory from your favorite text editor will be automatically available in the VM.

If you’d like to see what was installed in the VM, look in /vagrant/pg_config.sh.

In this class you will mostly be running your work in Python from the command line. In addition you’ll use the `psql` program to interact with the PostgreSQL database.

To connect `psql` to the forum database for Lesson 3, type `psql forum` at the command line. To exit psql, type `\q` or Control-D (^D).

[Lesson 4 Reference](reference.html)

### Normalize

* [See this article](http://www.bkent.net/Doc/simple5.htm)

#### Same number of columns in each row

In practice, the database system won't let us literally have different numbers of columns in different rows. But if we have columns that are sometimes empty (null) and sometimes not, or if we stuff multiple values into a single field, we're bending this rule.

The example to keep in mind here is the diet table from the zoo database. Instead of trying to stuff multiple foods for a species into a single row about that species, we separate them out. This makes it much easier to do aggregations and comparisons.

```
student_name | major
Afiya        | Computer Science
Afiya        | History
Habib        | Molecular Biology
```

#### Unique key

The key may be one column or more than one. It may even be the whole row, as in the diet table. But we don't have duplicate rows in a table.

More importantly, if we are storing non-unique facts — such as people's names — we distinguish them using a unique identifier such as a serial number. This makes sure that we don't combine two people's grades or parking tickets just because they have the same name.

```
create table students (
  id serial primary key
);

create table postal_places (
  postal_code text,
  country text,
  primary key (postal_code, country)
);
```

#### Facts that don't relate to the key belong in different columns

The example here was the items table, which had items, their locations, and the location's street addresses in it. The address isn't a fact about the item; it's a fact about the location. Moving it to a separate table saves space and reduces ambiguity, and we can always reconstitute the original table using a join.

Sort this out using `references` key word

```
create table sales (
  sku text references products (sku), -- (sku) isn't necessary since sku is same in both columns
  sale_date date,
  count integer
);
```

#### Don't imply relationships that don't exist

The example here was the job_skills table, where a single row listed one of a person's technology skills (like 'Linux') and one of their language skills (like 'French'). This made it look like their Linux knowledge was specific to French, or vice versa ... when that isn't the case in the real world. Normalizing this involved splitting the tech skills and job skills into separate tables.

```
name  | technology  | language
Hawa  | Linux       | Swahili
Hawa  | CSS         | French
```

### Types

`timestamp with time zone` is one... PostgreSQL has many useful types.

### Ideas

Can `JOIN` one table with itself:

```

SELECT a.id, b.id, a.building, a.room
       FROM residences AS a, residences AS b
 WHERE a.building = b.building
   AND a.room = b.room
   AND a.id != b.id
 ORDER BY a.building, a.room;

```

#### left join

Good if you want columns with a `COUNT` aggregate of `0`

#### Sub queries

`SELECT` from the result of a `SELECT`

```
select AVG(bigscore)
  FROM (
    SELECT MAX(score) AS bigscore
    FROM mooseball
    GROUP BY team )
  AS maxes; -- This AS statement is required for the sub query to work
```

Look up FROM syntax and scalar subqueries.

#### Views

A `SELECT` query stored in the database in a way that lets you use it like a
table

```
CREATE VIEW viewname AS SELECT ...

CREATE VIEW course_size AS
  SELECT course_id,
        COUNT(*) as num
  FROM enrollment
  GROUP BY course_id;
```
