class SuperClass(object):
    def call_a(self, a):
      print "Super call_a method"

class SubClass(SuperClass):
    def __init__(self):
      pass

    def call_a(self, a):
      if a == '1':
        print "Sub call_a method"
      else:
        return super(SubClass, self).call_a(a)

if __name__=='__main__':
	s1 = SubClass()
	s1.call_a(1)
