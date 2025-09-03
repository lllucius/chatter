Never worry about backwards compatibility.  It's not needed as this app hasn't been
deployed.  However, if you make a change that isn't backwards compatabile, make sure
that any other related/dependent code in the project is also updated.

Always use the existing unified cache interfaces when cache support is needed. It's
fine to create a specialization, but make sure it's warranted.

The project will be using:
 python 3.12+
 vite 7.1.3+
 react 19.1.1+
 postgresql 16.9+
 pgvector 0.6.2+


