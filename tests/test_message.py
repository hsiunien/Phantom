class Bird:


    agea = 1

    @agea.__setattr__("str",123)
    def agea(self, new_age):
        self.agea = new_age


b = Bird()
b.agea = 100
print(b.agea)
