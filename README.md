# AIRPLANE RESERVATION SITE
#### Video Demo:  <URL HERE>
#### Description:
##### OVERVIEW

My project is an airplane reservation site. It's a flask application. Main features that I implemented are:
- Database with airports, flights, user info and booked flights
- Ability to search through a database to find a flight
- Declaring number of adult and underage passengers
- declaring number of bags You wanna carry
- sending e-mail confirmation
- allowing payment via credit card
- registrating new user
- logging in and out
- editing your profile
- checking your booked flights

##### Database
I created a database with 4 tables:
- users
- flight
- booked
- airport

###### users

In my user table application is storing information about every registered user. Each user has his unique ID, username, First name, Surname, personal picture(which you can add after registration), password(that is kept in a hashed form) and e-mail address

###### flight

Each entry in flight table contains unique ID, id of an departure airport and arrival airport. As well as date of the flight ,departure hour ,landing hour and price.

###### booked

This table contains just 3 columns. Id of booked flight, id of an user who booked the flight and id of the flight.

###### airport

Airport table has 3 columns: ID of an airport, City where the airport is located, and name of the airport

##### HTML&CSS nad JavaScript

###### Layout
Whole project is build using bootstrap. In layout file (layout.html) are parts of each page that are the same. This includes navigation bar that have couple of links:
- link to Home Page
- link to booked flights if you are logged in
- link to register if you're not logged in
- link to log in if you're not already
- link to log out if you're logged in
- link to edit your profile if you are logged in

It also includes background image that I decided to be the same for every page.
In terms of style I decided to give my navigation bar dark gradient color

###### Main Page
On Main Page(index.html) We can see to forms. First form is to define search filters. We have there multiple inpust fields. First two inputs is a radio button group that enables us to decide if we want to fly only to destination or do we want to find return flight as well. If user is choosing to fly without return flight, input field with date of return becomes disabled using JavaScript and the arrow icon changes to one side arrow. 

Next fields determine our departure airport and arrival airport. In both of these fields we can choose from a list of airports that are added to database.

Next user is able to choose a date of departure. Obviously the earliest date that user can choose is the day of searching. When chosen the minimal value od return date is set to the same date( again using javascript).

Than we can choose how many adults are flying and how many underage people. In my airline underage passengers are flying for half of the full price.

There is also a submit button search for the flights. And this concludes first form

In second form we have the ability to choose from the list of flghts that fulfill our requirements. Each flight is described by:
- dpearture airport
- landing airport
- time of landing and time of departure
- calculated price

App also contains submit button to enable user to choose his flight

In terms of styling I decided to use opaque white coloring to distinct forms from rest of the page. I also decided to use borders to distinct each flight from another

###### Buy

On this page(buy.html) user can declare how many bags he will be carrying each bag cost 10 dollars. When user get to this page flight details are displayed(departure airport, landing airport, and hours of flight). Below is the number input when we decide  how many bags are being declared. using JavaScript the price is automatically changed to show current price.

###### charge 

On charge page(charge.html) user will see total amount to pay and button to proceed with paying with credit card. Obviously It's just a test app sa you csan enter false credit card information and it'll accept it

###### booked flight

On booked flights(bought.html) user can see a list of flights that he already purchased. He can see from and to what airport was the filght as well as date and time of flight

###### Profil

On user profile page(profil.html) user can see a form to change every data that he enetered during registration as well as ability to choose profile picture from his computer

###### login

This Page(login.html) contains a single form that prompts the user to enter his username and password

###### register

Registration page(register.html) contains a single form with several inputs:
- username
- email adress
- Name
- Surname
- Password
- Confirmation password

And submit button. Here we have client side validation so you can't submit form until every field is not empty and e-mail adress is in correct form

##### Python and flask(app.py)

###### Configuration

First of all I needed to configure 4 things:
- Connection to database
- Session
- Stripe payment client
- Mail client using mailtrap

###### Route ("/")

On this route I configured backside of a main page. All this route is practically doing is execute some queries to get data from database and give it to html.
It also prompts flash message when there are no flights on the chosen date

###### Route ("/buy")

This route renders buy.html. It GETs data from index.html and gives it back to buy.html to show the price

On the Post method it renders charge.html.

###### Route ("/charge")

 This route does 3 things. It computes payment using stripe. It sends a confirmation e-mail to the user who bought the ticket and it adds a record to booked table in database. When It's all done it redirects the user to his booked flights page

###### Route ("/bought")

This route gets all the flights from the booked table that logged in user bought. Than it gets details from other tables and renders a page with list of booked flights

###### Route ("/profil")

Get method of this route gets all the current data from user table and sends it to render a page with them as initial value.
Post method updates the database with new (after validation) information.

###### Route ("/logut")

It clears the session and shows flash message informing about logging out

###### Route ("/login")

GET methos renders a login.html page

POST method is validating entered data, creating session variables and showing flash messages according to situation

###### Route ("/upload")

This is the route resposible for uploading users profile picture and confirming the change with flash message

###### Route ("/register")

This route does a couple of things. First it renders register.html. Next it gets Inputed data and validate it on server side.
If everything is correct it adds an entry to users table, sends confirmation e-mail and show informing flash message






