---
title: Cephes Mathematical Library wrapped for Torch
layout: doc
---

#Cephes Mathematical Functions Library, wrapped for Torch

Provides and wraps the mathematical functions from the [Cephes mathematical library](http://www.netlib.org/cephes/), developed by [Stephen L. Moshier](http://www.moshier.net). This C library provides a <b>lot</b> of mathematical functions. It is used, among many other places, [at the heart of SciPy](https://github.com/scipy/scipy/tree/master/scipy/special/cephes).


##Example

###Simple call on a number

The wrapped functions can be called from Lua with the same synopsis as their C coutnerpart, and will then return a number, for example:

```lua
require 'cephes'
x = cephes.igam(2, 3) -- returns a number
```


###Calling on tensors

Our wrappers for cephes functions are vectorized, meaning they can 

* take tensors as arguments, evaluating the function for each element of the arguments, and return the result into a vector. 
* mix tensors and numbers as arguments, numbers are automatically expanded
* **shape does not matter**, only the number of elements.


Like most torch functions, they also accept an optional Tensor as first argument to store the result into.

```lua
require 'cephes'
-- Call over a whole tensor of parameters
result = cephes.ndtr(torch.randn(10)) -- returns a new tensor 
                                      -- of 10 elements

-- Several tensor arguments, pairing them map-like
-- Below returns a vector of 100 elements
x = torch.rand(100)
y = torch.rand(100)
result = cephes.igam(x, y)

-- Mix number and tensors: numbers are automatically expanded
-- Below returns a vector of 100 elements
result = cephes.igam(4, y)

-- Can also use matrices: only the number of elements matters
-- Below with a 3D array and a vector, return a vector of 100 elts
z = torch.rand(2,5,10)
result = cephes.igam(z, y)

-- And of course you can store the result into an 
-- existing tensor of the right number of elements
-- Below stores into an existing 3D tensors of 100 elements
result = torch.Tensor(2,5,10)
cephes.igam(result, x, y)
```

##Installation

From a terminal:

```bash
torch-rocks install cephes
```

##Error Handling

By default, Torch-Cephes **does not signal any error** (domain, singularity, overflow, underflow, precision). It is as non-intrusive as possible and tries to return a value which is hopefully usable: it might be NaN, it might be inf.

However, the user can ask Cephes to generate lua errors with the following functions.

###cephes.setErrorLevel(level)

Sets the level of error reporting.

>**Input:**  `level` : can be any of
>   - `'off'`/`0` to be entirely quiet
>   - `'error'`/`1` to issue Lua errors with stack trace
>   - `'warning'`/`2` to print a warning on stdout
>
>**Returns:** None

###cephes.getErrorLevel()

Returns the current level of error reporting, for example to save and restore later.

>**Input:**  None
>
>**Returns:** integer 0, 1, or 2, representing the current error reporting level, see `setErrorLevel()`


##List of Cephes functions

See [the full list of Cephes double-precision functions](doubldoc.html). The Torch wrappers respect the same prototypes. 

**Note**: a few features of the original library have not been wrapped:

* single-precision functions: due to a few name clashes with their double counterparts, they require a slightly larger effort to wrap. Please [fill a feature request](https://github.com/jucor/torch-cephes/issues/new) if you need them.
* polynomials with rational coefficients: their names clash with the polynomials with double coefficients. We wrapped the latter, which seem more generally useful, but please [raise an issue](ahttps://github.com/jucor/torch-cephes/issues/new).
* linear algebra functions: torch already has those.

So, here goes the whole list, click for details:

* **acosh**, [Inverse hyperbolic cosine](doubldoc.html#acosh)
* **airy**, [Airy functions](doubldoc.html#airy)
* **asin**, [Inverse circular sine](doubldoc.html#asin)
* **acos**, [Inverse circular cosine](doubldoc.html#acos)
* **asinh**, [Inverse hyperbolic sine](doubldoc.html#asinh)
* **atan**, [Inverse circular tangent](doubldoc.html#atan)
* **atan2**, [Quadrant correct inverse circular tangent](doubldoc.html#atan2)
* **atanh**, [Inverse hyperbolic tangent](doubldoc.html#atanh)
* **bdtr**, [Binomial distribution](doubldoc.html#bdtr)
* **bdtrc**, [Complemented binomial distribution](doubldoc.html#bdtrc)
* **bdtri**, [Inverse binomial distribution](doubldoc.html#bdtri)
* **beta**, [Beta function](doubldoc.html#beta)
* **btdtr**, [Beta distribution](doubldoc.html#btdtr)
* **cbrt**, [Cube root](doubldoc.html#cbrt)
* **chbevl**, [Evaluate Chebyshev series](doubldoc.html#chbevl)
* **chdtr**, [Chi-square distribution](doubldoc.html#chdtr)
* **chdtrc**, [Complemented Chi-square distribution](doubldoc.html#chdtrc)
* **chdtri**, [Inverse of complemented Chi-square distribution](doubldoc.html#chdtri)
* **cheby**, [Find Chebyshev coefficients](doubldoc.html#cheby)
* **clog**, [Complex natural logarithm](doubldoc.html#clog)
* **cexp**, [Complex exponential function](doubldoc.html#cexp)
* **csin**, [Complex circular sine](doubldoc.html#csin)
* **ccos**, [Complex circular cosine](doubldoc.html#ccos)
* **ctan**, [Complex circular tangent](doubldoc.html#ctan)
* **ccot**, [Complex circular cotangent](doubldoc.html#ccot)
* **casin**, [Complex circular arc sine](doubldoc.html#casin)
* **cacos**, [Complex circular arc cosine](doubldoc.html#cacos)
* **catan**, [Complex circular arc tangent](doubldoc.html#catan)
* **csinh**, [Complex hyperbolic sine](doubldoc.html#csinh)
* **casinh**, [Complex inverse hyperbolic sine](doubldoc.html#casinh)
* **ccosh**, [Complex hyperbolic cosine](doubldoc.html#ccosh)
* **cacosh**, [Complex inverse hyperbolic cosine](doubldoc.html#cacosh)
* **ctanh**, [Complex hyperbolic tangent](doubldoc.html#ctanh)
* **catanh**, [Complex inverse hyperbolic tangent](doubldoc.html#catanh)
* **cpow**, [Complex power function](doubldoc.html#cpow)
* **cmplx**, [Complex number arithmetic](doubldoc.html#cmplx)
* **cabs**, [Complex absolute value](doubldoc.html#cabs)
* **csqrt**, [Complex square root](doubldoc.html#csqrt)
* **const**, [Globally declared constants](doubldoc.html#const)
* **cosh**, [Hyperbolic cosine](doubldoc.html#cosh)
* **dawsn**, [Dawson's Integral](doubldoc.html#dawsn)
* **drand**, [Pseudorandom number generator](doubldoc.html#drand)
* **ei**, [Exponential Integral](doubldoc.html#ei)
* **eigens**, [Eigenvalues and eigenvectors of a real symmetric matrix](doubldoc.html#eigens)
* **ellie**, [Incomplete elliptic integral of the second kind](doubldoc.html#ellie)
* **ellik**, [Incomplete elliptic integral of the first kind](doubldoc.html#ellik)
* **ellpe**, [Complete elliptic integral of the second kind](doubldoc.html#ellpe)
* **ellpj**, [Jacobian elliptic functions](doubldoc.html#ellpj)
* **ellpk**, [Complete elliptic integral of the first kind](doubldoc.html#ellpk)
* **euclid**, [Rational arithmetic routines](doubldoc.html#euclid)
* **exp**, [Exponential function](doubldoc.html#exp)
* **exp10**, [Base 10 exponential function](doubldoc.html#exp10)
* **exp2**, [Base 2 exponential function](doubldoc.html#exp2)
* **expn**, [Exponential integral En](doubldoc.html#expn)
* **expx2**, [Exponential of squared argument](doubldoc.html#expx2)
* **fabs**, [Absolute value](doubldoc.html#fabs)
* **fac**, [Factorial function](doubldoc.html#fac)
* **fdtr**, [F distribution](doubldoc.html#fdtr)
* **fdtrc**, [Complemented F distribution](doubldoc.html#fdtrc)
* **fdtri**, [Inverse of complemented F distribution](doubldoc.html#fdtri)
* **fftr**, [Fast Fourier transform](doubldoc.html#fftr)
* **floor**, [Floor function](doubldoc.html#floor)
* **ceil**, [Ceil function](doubldoc.html#ceil)
* **frexp**, [Extract exponent](doubldoc.html#frexp)
* **ldexp**, [Apply exponent](doubldoc.html#ldexp)
* **fresnl**, [Fresnel integral](doubldoc.html#fresnl)
* **gamma**, [Gamma function](doubldoc.html#gamma)
* **lgam**, [Natural logarithm of gamma function](doubldoc.html#lgam)
* **gdtr**, [Gamma distribution function](doubldoc.html#gdtr)
* **gdtrc**, [Complemented gamma distribution function](doubldoc.html#gdtrc)
* **gels**, [Linear system with symmetric coefficient matrix](doubldoc.html#gels)
* **hyp2f1**, [Gauss hypergeometric function](doubldoc.html#hyp2f1)
* **hyperg**, [Confluent hypergeometric function](doubldoc.html#hyperg)
* **i0**, [Modified Bessel function of order zero](doubldoc.html#i0)
* **i0e**, [Exponentially scaled modified Bessel function of order zero](doubldoc.html#i0e)
* **i1**, [Modified Bessel function of order one](doubldoc.html#i1)
* **i1e**, [Exponentially scaled modified Bessel function of order one](doubldoc.html#i1e)
* **igam**, [Incomplete gamma integral](doubldoc.html#igam)
* **igamc**, [Complemented incomplete gamma integral](doubldoc.html#igamc)
* **igami**, [Inverse of complemented imcomplete gamma integral](doubldoc.html#igami)
* **incbet**, [Incomplete beta integral](doubldoc.html#incbet)
* **incbi**, [Inverse of imcomplete beta integral](doubldoc.html#incbi)
* **isnan**, [Test for not a number](doubldoc.html#isnan)
* **isfinite**, [Test for infinity](doubldoc.html#isfinite)
* **signbit**, [Extract sign](doubldoc.html#signbit)
* **iv**, [Modified Bessel function of noninteger order](doubldoc.html#iv)
* **j0**, [Bessel function of order zero](doubldoc.html#j0)
* **y0**, [Bessel function of the second kind, order zero](doubldoc.html#y0)
* **j1**, [Bessel function of order one](doubldoc.html#j1)
* **y1**, [Bessel function of the second kind, order one](doubldoc.html#y1)
* **jn**, [Bessel function of integer order](doubldoc.html#jn)
* **jv**, [Bessel function of noninteger order](doubldoc.html#jv)
* **k0**, [Modified Bessel function, third kind, order zero](doubldoc.html#k0)
* **k0e**, [Modified Bessel function, third kind, order zero, exponentially scaled](doubldoc.html#k0e)
* **k1**, [Modified Bessel function, third kind, order one](doubldoc.html#k1)
* **k1e**, [Modified Bessel function, third kind, order one, exponentially scaled](doubldoc.html#k1e)
* **kn**, [Modified Bessel function, third kind, integer order](doubldoc.html#kn)
* **kolmogorov**, [Kolmogorov, Smirnov distributions](doubldoc.html#kolmogorov)
* **levnsn**, [Linear predictive coding](doubldoc.html#levnsn)
* **lmdif**, [Levenberg-Marquardt algorithm](doubldoc.html#lmdif)
* **log**, [Natural logarithm](doubldoc.html#log)
* **log10**, [Common logarithm](doubldoc.html#log10)
* **log2**, [Base 2 logarithm](doubldoc.html#log2)
* **lrand**, [Pseudorandom integer number generator](doubldoc.html#lrand)
* **lsqrt**, [Integer square root](doubldoc.html#lsqrt)
* **minv**, [Matrix inversion](doubldoc.html#minv)
* **mtransp**, [Matrix transpose](doubldoc.html#mtransp)
* **nbdtr**, [Negative binomial distribution](doubldoc.html#nbdtr)
* **nbdtrc**, [Complemented negative binomial distribution](doubldoc.html#nbdtrc)
* **nbdtri**, [Functional inverse of negative binomial distribution](doubldoc.html#nbdtri)
* **ndtr**, [Normal distribution function](doubldoc.html#ndtr)
* **erf**, [Error function](doubldoc.html#erf)
* **erfc**, [Complementary error function](doubldoc.html#erfc)
* **ndtri**, [Inverse of normal distribution function](doubldoc.html#ndtri)
* **pdtr**, [Poisson distribution function](doubldoc.html#pdtr)
* **pdtrc**, [Complemented Poisson distribution function](doubldoc.html#pdtrc)
* **pdtri**, [Inverse of Poisson distribution function](doubldoc.html#pdtri)
* **planck**, [Integral of Planck's black body radiation formula](doubldoc.html#planck)
* **polevl**, [Evaluate polynomial](doubldoc.html#polevl)
* **p1evl**, [Evaluate polynomial](doubldoc.html#p1evl)
* **polmisc**, [Functions of a polynomial](doubldoc.html#polmisc)
* **polrt**, [Roots of a polynomial](doubldoc.html#polrt)
* **polylog**, [Polylogarithms](doubldoc.html#polylog)
* **polyn**, [Arithmetic operations on polynomials](doubldoc.html#polyn)
* **pow**, [Power function](doubldoc.html#pow)
* **powi**, [Integer power function](doubldoc.html#powi)
* **psi**, [Psi (digamma) function](doubldoc.html#psi)
* **revers**, [Reversion of power series](doubldoc.html#revers)
* **rgamma**, [Reciprocal gamma function](doubldoc.html#rgamma)
* **round**, [Round to nearest or even integer](doubldoc.html#round)
* **shichi**, [Hyperbolic sine and cosine integrals](doubldoc.html#shichi)
* **sici**, [Sine and cosine integrals](doubldoc.html#sici)
* **simpsn**, [Numerical integration of tabulated function](doubldoc.html#simpsn)
* **simq**, [Simultaneous linear equations](doubldoc.html#simq)
* **sin**, [Circular sine](doubldoc.html#sin)
* **cos**, [Circular cosine](doubldoc.html#cos)
* **sincos**, [Sine and cosine by interpolation](doubldoc.html#sincos)
* **sindg**, [Circular sine of angle in degrees](doubldoc.html#sindg)
* **cosdg**, [Circular cosine of angle in degrees](doubldoc.html#cosdg)
* **sinh**, [Hyperbolic sine](doubldoc.html#sinh)
* **spence**, [Dilogarithm](doubldoc.html#spence)
* **sqrt**, [Square root](doubldoc.html#sqrt)
* **stdtr**, [Student's t distribution](doubldoc.html#stdtr)
* **stdtri**, [Functional inverse of Student's t distribution](doubldoc.html#stdtri)
* **struve**, [Struve function](doubldoc.html#struve)
* **tan**, [Circular tangent](doubldoc.html#tan)
* **cot**, [Circular cotangent](doubldoc.html#cot)
* **tandg**, [Circular tangent of argument in degrees](doubldoc.html#tandg)
* **cotdg**, [Circular cotangent of argument in degrees](doubldoc.html#cotdg)
* **tanh**, [Hyperbolic tangent](doubldoc.html#tanh)
* **log1p**, [Relative error logarithm](doubldoc.html#log1p)
* **expm1**, [Relative error exponential](doubldoc.html#expm1)
* **cosm1**, [Relative error cosine](doubldoc.html#cosm1)
* **yn**, [Bessel function of second kind of integer order](doubldoc.html#yn)
* **zeta**, [Zeta function of two arguments](doubldoc.html#zeta)
* **zetac**, [Riemann zeta function of two arguments](doubldoc.html#zetac)

##List of Torch-only functions

Those functions are not part of the original Cephes library

###cephes.digamma(x)

Alias for `cephes.psi(x)`

###cephes.polygamma(m, x)

The `(m+1)`-th derivative of the logarithm of the gamma function [(see MathWorld definition)](http://mathworld.wolfram.com/PolygammaFunction.html).

>**Input:** 
>
> * `m` : non-negative integer
> * `x` : real number
>
>**Returns:** `(m+1)`-th derivative of the logarithm of the gamma function, evaluated at `x`

###cephes.betagrad(x, y)

The partial-derivative of the beta function, with respect to the first variable.

>**Input:** 
>
> * `x` : positive real number
> * `y` : positive real number
>
>**Returns:** Partial-derivative of the beta function with respect to the first variable, evaluated at (`x`, `y`)

##Limits

Convenience functions to check for finiteness.

###cephes.nan
Stands for not a number, clearer alias for `0/0` 

###cephes.isnan(x)
Checks if `x` is not a number.

>**Input:** `x` : any number
>
>**Returns:** `true` if `x` is `cephes.nan`, `false` otherwise


###cephes.isinf(x)
Checks is a number is infinite.

>**Input:** `x` : any number
>
>**Returns:**** `true` if `x` is `math.huge` or `-math.huge` or `cephes.nan`, `false` otherwise.

###cephes.isfinite(x)
Checks if a number is finite.

>**Input:**  `x` : any number
>
>**Returns:**  `not cephes.isinf(x) and not cephes.isnan(x)`

##Complex numbers

###cephes.new_cmplx(re, im)
>**Input:** 
>
> * `re` : any number, to initialize the real part
> * `im` : any number, to initalize the imaginary part
>
>**Returns:** a pointer to a new Cephes FFI complex number with real part `r` and imaginary part `im`.

##Unit Tests

Last but not least, the unit tests are in the folder
[`luasrc/tests`](https://github.com/jucor/torch-cephes/tree/master/luasrc/tests). You can run them from your local clone of the repostiory with:

```bash
git clone https://www.github.com/jucor/torch-cephes
find torch-cephes/luasrc/tests -name "test*lua" -exec torch {} \;
```

Those tests will soone be automatically installed with the package, once I sort out a bit of CMake resistance.

##Direct access to FFI

###cephes.ffi.*

Functions directly accessible at the top of the `cephes` table are Lua wrappers to the actual C functions from Cephes, with extra error checking. If, for any reason, you want to get rid of this error checking and of a possible overhead, the FFI-wrapper functions can be called directly via `cephes.ffi.myfunction()` instead of `cephes.myfunction()`.
