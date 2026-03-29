# Defined Protocol

```json
{
  "action": "broadcast",
  "from": "foo", 
  "to": "all", 
  "msg": "Hi!" 
}
// "action": "broadcast" will send msg to all user, "to" field can be empty

{ 
  "action": "chat", 
  "from": "foo", 
  "to": "bar", 
  "msg": "Hi!" 
}
// "action": "chat" will send msg to specific user, "to" field can not be empty

{ 
  "action": "gretting", 
  "from": "foo", 
}
// "action": "gretting" for server can track user message
```

When client send message, assume that first 4 bytes is JSON string length
