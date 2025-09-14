Never try to keep code backwards compatible!!!  It's is not wanted or needed.  In my
opinion it can prevent the right decisions on new code changes.

Always use the existing core caching system. It can be augmented if needed, but do
not create an overlapping system.

Always use the existing rate limiting system. It can be augmented if needed, but do
not create an overlapping system.

Always use the existing monitoring system. It can be augmented if needed, but do
not create an overlapping system.

Always use the existing event system. It can be augmented if needed, but do
not create an overlapping system.

Always use the existing validation system. It can be augmented if needed, but do
not create an overlapping system. 

ALWAYS, I repeat, ALWAYS look for existing classes, interfaces, systems, etc. For example, if you need to add monitoring to an API, look for an established monitoring system.  You may modify it if needed, but DO NOT create another.  The intent here is to keep duplication out of the code and checking before making updates will reduce the amount of rewriting leter.

Fir "id" type fields, this project uses ULIDs, NOT UUIDs!

The project will be using:
 python 3.12+
 vite 7.1.3+
 react 19.1.1+
 postgresql 16.9+
 pgvector 0.6.2+

Reiterating...Never create backwards compatibility layers!!!  Always update code to use new interfaces.

