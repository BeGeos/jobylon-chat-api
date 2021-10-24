# API DOCUMENTATION

## Main Routes

### Users:

- _/api/users_
- _/api/users/:user_id_

### Chat:

- _/api/chat_
- _/api/chat/:chat_id_

## Users

- **/api/users**
- **/api/users/:user_id**

This route accepts 2 methods:
**GET** and **POST**

A GET request to _/api/users_ will return all the users (admin, and superusers excluded).

If a parameter is passed in _:user_id_ it will return
only the user with that id.

If successful both these operations will return a status code of 200/OK.

---

A POST request to _/api/users_ will create a new user in the database. There is only one parameter required in the body => username.

Since authentication is not enforced there is no need for a
password. Every other parameter in the request will be ignored.
A successful response will carry a 201/CREATED code.

To save yourself some time you can pass in the URL a populate
parameter, specifying the size as integer number. If the number is greater than 100, 100 will be used.

This will trigger a populate command in the database of random users (from the [Random Data API] (https://random-data-api.com/)) in number = to the parameter passed in.

**WARNING: every populate action will delete all the previous users (admin excluded) and create a new set of users**

An example is **POST** _/api/users?populate=20_ will return a 201/CREATED code, if successful and a _"20 users created"_ message.

---

### Errors

Error will carry a status code and an object with a message. Cases for errors are:

- Username already exists: **400 - Bad Request**
- Username is not in the POST request body: **400 Bad Request**
- Populate is not an integer: **422 Unprocessable Entity**
- User with _user_id_ does not exist: **404 User not Found**
- Internal Errors: **500** and a message

## Chat

- **/api/chat**
- **/api/chat/:chat_id**

This route accepts 2 methods:
**GET** and **POST**

A GET request to _/api/chat_ will return an error. To work this method needs to make a request with a _:chat_id_ and also a _user_ query parameter.

e.g _GET /api/chat/:chat_id?user={username}_

This ensures that you know the UUID of the chat and that the user belongs to the conversation. A user cannot read messages of a chat they are not part of.

A successful response will return a 200/OK code and a JSON object with:

- _id_ : ID of the chat
- _timestamp_ : the date of creation of the chat
- _members_ : a list with the 2 unique members of the conversation
- _messages_ : a list of objects with message

Each message in has an _author_, a _timestamp_ and the _content_

POST requests need to be sent to the _/api/chat_ URL. There are 3 required parameter that need to be sent in the body:

- _sender_ => Username of the user sending the message
- _receiver_ => Username of the user receiving the message
- _content_ => The content of the message

The logic behind will take care of fetching the correct chat, and if the chat already exists, based on the 2 unique members, it will use that same chat. Otherwise, it will create a new one, if one does not exist.

This is URL will "send" a message to the receiver, adding a message to the chat itself. For the receiver to see the message, or messages on the chat, they need to make a GET request using _/api/chat/:chat_id?user=username_

Chat IDs are UUIDs made of 32 hexadecimal characters to add security. In fact, to fetch a chat one needs to know precisely the chat id. Every time a message is successfully sent a 201/CREATED code and a JSON object will be returned. In the JSON there will be a complete snapshot of the chat, chat id included.

---

### Errors

A list of possible errors. They will return with a status code and a message:

- if the _:chat_id_ doesn't exist: **404 Not Found**
- If the user is not provided, OR the user doesn't belong to the members of the chat: **401 Unauthorised**
- If the sender and receiver are the same: **400 Bad Request**
- If the receiver doesn't exist: **400 Bad Request**
- Generic Internal Errors: **500** status code and a message
