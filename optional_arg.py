def call_func(arg1, arg2=None):
	print arg1
	print arg2

call_func(1)
call_func(1,10)
try:
	call_func()
except Exception, e:
	print "Encounterd exception."
