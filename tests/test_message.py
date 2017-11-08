from  app.message import FlashMessage
from  itsdangerous import TimedJSONWebSignatureSerializer as ts

t = ts("55511332", 3200)
tk = t.dumps({"zens53@163.com": 2})
print(tk)
