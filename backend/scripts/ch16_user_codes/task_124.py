FIXED_PASCAL = """type
  TNotification = class
    function Send: string; virtual;
  end;

  TEmailNotification = class(TNotification)
    function Send: string; override;
  end;

  TSmsNotification = class(TNotification)
    function Send: string; override;
  end;

function TNotification.Send: string;
begin
  Send := 'message';
end;

function TEmailNotification.Send: string;
begin
  Send := 'email';
end;

function TSmsNotification.Send: string;
begin
  Send := 'sms';
end;

var
  items: array[1..2] of TNotification;
  i: integer;
begin
  items[1] := TEmailNotification.Create;
  items[2] := TSmsNotification.Create;

  for i := 1 to 2 do
    writeln(items[i].Send);
end."""

BUGGY_PASCAL = """type
  TNotification = class
    function Send: string;
  end;

  TEmailNotification = class(TNotification)
    function SendText: string; override;
  end;

  TSmsNotification = class(TNotification)
    function Send: integer; override;
  end;

function TNotification.Send: string;
begin
  Send := 'message';
end;

function TEmailNotification.SendText: string;
begin
  SendText := 'email';
end;

function TSmsNotification.Send: integer;
begin
  Send := 1;
end;

var
  items: array[1..2] of TNotification;
begin
  items[1] := TEmailNotification.Create;
  items[2] := TSmsNotification.Create;

  for item in items do
    Console.WriteLine(item.Send());
end."""

FIXED_PYTHON = """class Notification:
    def send(self):
        return "message"


class EmailNotification(Notification):
    def send(self):
        return "email"


class SmsNotification(Notification):
    def send(self):
        return "sms"


items = [EmailNotification(), SmsNotification()]

for item in items:
    print(item.send())"""

BUGGY_PYTHON = """class Notification
    def send(self):
        return "message"


class EmailNotification(Notification):
    def Send(self):
        return "email"


class SmsNotification(Notification):
    def send():
        return "sms"


items = [EmailNotification(), SmsNotification()]

for item in items:
    Console.WriteLine(item.send())"""

FIXED_CPP = """#include <iostream>
#include <string>
#include <vector>

class Notification {
public:
    virtual std::string send() {
        return "message";
    }
};

class EmailNotification : public Notification {
public:
    std::string send() override {
        return "email";
    }
};

class SmsNotification : public Notification {
public:
    std::string send() override {
        return "sms";
    }
};

int main() {
    std::vector<Notification*> items = {
        new EmailNotification(),
        new SmsNotification()
    };

    for (Notification* item : items) {
        std::cout << item->send() << '\\n';
    }

    return 0;
}"""

BUGGY_CPP = """#include <iostream>
#include <vector>

class Notification {
public:
    std::string send() {
        return "message";
    }
};

class EmailNotification : public Notification {
public:
    string Send() override {
        return "email";
    }
};

class SmsNotification : public Notification {
public:
    int send() override {
        return 1;
    }
};

int main() {
    vector<Notification> items = {
        EmailNotification(),
        SmsNotification()
    };

    for (auto item : items) {
        Console.WriteLine(item.send());
    }

    return 0;
}"""

FIXED_CSHARP = """using System;

class Notification {
    public virtual string Send() {
        return "message";
    }
}

class EmailNotification : Notification {
    public override string Send() {
        return "email";
    }
}

class SmsNotification : Notification {
    public override string Send() {
        return "sms";
    }
}

Notification[] items = {
    new EmailNotification(),
    new SmsNotification()
};

foreach (Notification item in items) {
    Console.WriteLine(item.Send());
}"""

BUGGY_CSHARP = """using System;

class Notification {
    public string Send() {
        return "message";
    }
}

class EmailNotification : Notification {
    public override string SendMessage() {
        return "email";
    }
}

class SmsNotification : Notification {
    public override int Send() {
        return 1;
    }
}

Notification[] items = {
    EmailNotification(),
    SmsNotification()
};

for item in items:
    print(item.Send());"""

FIXED_JAVA = """class Notification {
    String send() {
        return "message";
    }
}

class EmailNotification extends Notification {
    @Override
    String send() {
        return "email";
    }
}

class SmsNotification extends Notification {
    @Override
    String send() {
        return "sms";
    }
}

class Main {
    public static void main(String[] args) {
        Notification[] items = {
            new EmailNotification(),
            new SmsNotification()
        };

        for (Notification item : items) {
            System.out.println(item.send());
        }
    }
}"""

BUGGY_JAVA = """class Notification {
    String send() {
        return "message";
    }
}

class EmailNotification extends Notification {
    @Override
    String Send() {
        return "email";
    }
}

class SmsNotification extends Notification {
    @Override
    int send() {
        return 1;
    }
}

class Main {
    public static void main(String[] args) {
        Notification[] items = {
            EmailNotification(),
            SmsNotification()
        };

        foreach (Notification item in items) {
            Console.WriteLine(item.send());
        }
    }
}"""
