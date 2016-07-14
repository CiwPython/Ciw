.. _setting-seeds:

=============
Setting Seeds
=============

The Ciw function :code:`ciw.seed` can be used to ensure reproducibility of results. As Ciw uses random number streams from both the :code:`random` and :code:`numpy` modules, this function simply sets the seeds for these.

    >>> ciw.seed(5) # doctest:+SKIP