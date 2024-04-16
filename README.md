# Introduction
This project shows attempts to study data on comsumer complaints about financial services like credit reporting, loans etc. The data was obtained from Kaggle (https://www.kaggle.com/datasets/anoopjohny/consumer-complaint-database). Furthermore, since the query responses used to study this data can reveal sensitive information, we implement a privacy preserving system to run predetermined queries. We use the Laplace mechanism to obtain differentially private results for our queries. We use PostgreSQL to store and query the data.

# Creating the database and running queries
In order to run the code, a postgres database must be set up on the machine. 
Steps:
<ol>
<li> Download and install postgres.
<li> Create a database named "cc151"
<li> Use the following shell command to create the database:
CREATE DATABASE cc151
<li> Connect to the cc151 database
<li> Use the following command to create the 'complaints' table:
``
CREATE TABLE complaints(
    date DATE NOT NULL, 
    product VARCHAR(75) NOT NULL,
    subproduct VARCHAR(48) NOT NULL,
    issue VARCHAR(81) NOT NULL,
    subissue VARCHAR(141) NOT NULL,
    complaint VARCHAR(32440) NOT NULL,
    company_response_public VARCHAR(120) NOT NULL,
    company VARCHAR(88) NOT NULL,
    state VARCHAR(37) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    tags VARCHAR(30) NOT NULL,
    consent VARCHAR(28) NOT NULL,
    submitted_via VARCHAR(15) NOT NULL,
    date_sent VARCHAR(22) NOT NULL,
    company_response_consumer VARCHAR(33) NOT NULL,
    timely_reponse VARCHAR(18) NOT NULL,
    consumer_disputed VARCHAR(20) NOT NULL,
    complaint_id SERIAL PRIMARY KEY
    )
``
<li> Use the following command to copy data into table, replacing X in the path with the directory where this repository is cloned:

\copy 'complaints' from 'X/CS 151 Term Project/database_priv/data/cleaned_data.csv' delimiter ' ' CSV HEADER;

<li> Run each of step A-D separately and in order, to see query results and runtime and error plots.
</ol>

# Here are the following SQL queries we intend to use:

## Q1:
### Which company. subproduct pairs have >200 complaints.
select * from (select company, product, count(*) ct
from complaints
group by company, product)
where ct > 200

## Q2:
### Which subproducts are most complained about?    
with X as (select subproduct, count(*) ct from
		  complaints group by subproduct)
select * from X
order by ct desc

## Q3
### Where can Massachusettes consumers purchase credit reporting services?
with Z as (with X as (select distinct company, state, zip_code, count(*) ct from
complaints 
where subproduct=' Credit reporting'
		  group by company, state, zip_code)
select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat
from X, (select distinct company, state, zip_code, count(*) ct from
complaints group by company, state, zip_code)Y
where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code)
select company, state, zip_code, rat
from Z
where rat < 0.2 and state=' MA'

## Q4: 
### Where can Florida consumers purchase credit reporting services?
with Z as (with X as (select distinct company, state, zip_code, count(*) ct from
complaints 
where subproduct=' Credit reporting'
		  group by company, state, zip_code)
select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat
from X, (select distinct company, state, zip_code, count(*) ct from
complaints group by company, state, zip_code)Y
where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code)
select company, state, zip_code, rat
from Z
where rat < 0.2 and state=' FL'

## Q5: 
### Where can Texas consumers purchase credit reporting services?
with Z as (with X as (select distinct company, state, zip_code, count(*) ct from
complaints 
where subproduct=' Credit reporting'
		  group by company, state, zip_code)
select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat
from X, (select distinct company, state, zip_code, count(*) ct from
complaints group by company, state, zip_code)Y
where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code)
select company, state, zip_code, rat
from Z
where rat < 0.2 and state=' TX'

# Privacy Preservation
The queries run above reveal sensitive information about companies, like which of their products at which specific locations receive consumer complaints.
We use the Laplace Mechanism to make the query responses differentially private.
We use a sensitivity of 1 since all of the above queries are mainly count queries.
We use epsilon values [0.01, 0.02, 0.03, 0.04, 0.05]. These were chosen since they are all greater than the epsilon we would need to distort outliers of the data. We computes outlier-distorting epsilons using the relationship Var = (2*GS/Epsilon^2), where Var = variance of the data, GS (global sensitivty) = 1. We picked the epsilon values used, to be larger than the ones computed, to preserve more accuracy.

