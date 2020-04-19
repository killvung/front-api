# Front-API 
This is the API backend for [Front](https://killvung.github.io/nuxt-front/), a system I am developing to track down my walking statistics over Austin in the year of 2019.

In order to speed up the development process with confident, I use Flask-base boilerpalte which can found it [here](https://github.com/hack4impact/flask-base)

## Overall diagram
The backend reads data from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (a hosting service offered by MongoDB) then send data to NodeJS's Express Apollo GraphQL server to process the data. 


