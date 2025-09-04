Never try to keep code backwards compatible!!!  It's is not wanted or needed.  In my
opinion it can prevent the right decisions on new code changes.

Always use the existing core caching system when cache support is needed. It's fine
to create a specialization, but make sure it's warranted.

Always use the existing rate limiting system when rate limiting is needed.

The project will be using:
 python 3.12+
 vite 7.1.3+
 react 19.1.1+
 postgresql 16.9+
 pgvector 0.6.2+


