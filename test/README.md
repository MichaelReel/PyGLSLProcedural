
To test with python2, use the back port of the python mock standard library

> python -m pip install mock

To get coverage install the coverage library/script

> python -m pip install coverage

From the command line it's possible to run the tests and produce coverage

> cd test
> coverage run test.py
> coverage html

The html description of coverage should now be in test/htmlcov