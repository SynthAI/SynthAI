require 'totem'
require 'distributions'
require 'pl.strict'

local myTests = {}
local notRun = {}
local tester = totem.Tester()
torch.manualSeed(1234567890)

local function sidakCorrection(alpha, n)
    -- Sidak correction is good for independent tests -- which we have here.
    return 1 - math.pow((1-alpha), 1/n)
end
-- This is the significance threshold for the statistical tests, i.e. close to 0
local statisticalTests = 57
local alpha = sidakCorrection(.05, statisticalTests)

local standardGaussianPDFWindow = torch.Tensor({
    {0.058549831524319, 0.070096874908772, 0.080630598589333, 0.089110592667962, 0.094620883979159, 0.096532352630054, 0.094620883979159, 0.089110592667962, 0.080630598589333, 0.070096874908772, 0.058549831524319},
    {0.070096874908772, 0.083921195741359, 0.096532352630054, 0.106684748780159, 0.113281765213783, 0.115570208671698, 0.113281765213783, 0.106684748780159, 0.096532352630054, 0.083921195741359, 0.070096874908772},
    {0.080630598589333, 0.096532352630054, 0.111038635972398, 0.122716671259482, 0.130305046413711, 0.132937382963516, 0.130305046413711, 0.122716671259482, 0.111038635972398, 0.096532352630054, 0.080630598589333},
    {0.089110592667962, 0.106684748780159, 0.122716671259482, 0.135622896239029, 0.144009347774931, 0.146918529576363, 0.144009347774931, 0.135622896239029, 0.122716671259482, 0.106684748780159, 0.089110592667962},
    {0.094620883979159, 0.113281765213783, 0.130305046413711, 0.144009347774931, 0.152914388511582, 0.156003464068888, 0.152914388511582, 0.144009347774931, 0.130305046413711, 0.113281765213783, 0.094620883979159},
    {0.096532352630054, 0.115570208671698, 0.132937382963516, 0.146918529576363, 0.156003464068888, 0.159154943091895, 0.156003464068888, 0.146918529576363, 0.132937382963516, 0.115570208671698, 0.096532352630054},
    {0.094620883979159, 0.113281765213783, 0.130305046413711, 0.144009347774931, 0.152914388511582, 0.156003464068888, 0.152914388511582, 0.144009347774931, 0.130305046413711, 0.113281765213783, 0.094620883979159},
    {0.089110592667962, 0.106684748780159, 0.122716671259482, 0.135622896239029, 0.144009347774931, 0.146918529576363, 0.144009347774931, 0.135622896239029, 0.122716671259482, 0.106684748780159, 0.089110592667962},
    {0.080630598589333, 0.096532352630054, 0.111038635972398, 0.122716671259482, 0.130305046413711, 0.132937382963516, 0.130305046413711, 0.122716671259482, 0.111038635972398, 0.096532352630054, 0.080630598589333},
    {0.070096874908772, 0.083921195741359, 0.096532352630054, 0.106684748780159, 0.113281765213783, 0.115570208671698, 0.113281765213783, 0.106684748780159, 0.096532352630054, 0.083921195741359, 0.070096874908772},
    {0.058549831524319, 0.070096874908772, 0.080630598589333, 0.089110592667962, 0.094620883979159, 0.096532352630054, 0.094620883979159, 0.089110592667962, 0.080630598589333, 0.070096874908772, 0.058549831524319}
})

local nonStandardGaussianPDFWindow = torch.Tensor({
    {0.000001452200915, 0.000000080797552, 0.000000000487159, 0.000000000000318, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000},
    {0.000240854107924, 0.000079287483413, 0.000002828501156, 0.000000010934760, 0.000000000004581, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000},
    {0.004328949915153, 0.008431643111764, 0.001779684515109, 0.000040707551309, 0.000000100903931, 0.000000000027105, 0.000000000000001, 0.000000000000000, 0.000000000000000, 0.000000000000000, 0.000000000000000},
    {0.008431643111764, 0.097167482167606, 0.121347500208756, 0.016422598310807, 0.000240854107924, 0.000000382796005, 0.000000000065930, 0.000000000000001, 0.000000000000000, 0.000000000000000, 0.000000000000000},
    {0.001779684515109, 0.121347500208756, 0.896643486507501, 0.717975976728288, 0.062301883958987, 0.000585859662884, 0.000000597017644, 0.000000000065930, 0.000000000000001, 0.000000000000000, 0.000000000000000},
    {0.000040707551309, 0.016422598310807, 0.717975976728288, 3.401567607740293, 1.746423041360607, 0.097167482167607, 0.000585859662884, 0.000000382796005, 0.000000000027105, 0.000000000000000, 0.000000000000000},
    {0.000000100903931, 0.000240854107924, 0.062301883958987, 1.746423041360608, 5.305164769729846, 1.746423041360607, 0.062301883958987, 0.000240854107924, 0.000000100903931, 0.000000000004581, 0.000000000000000},
    {0.000000000027105, 0.000000382796005, 0.000585859662884, 0.097167482167607, 1.746423041360611, 3.401567607740294, 0.717975976728288, 0.016422598310807, 0.000040707551309, 0.000000010934760, 0.000000000000318},
    {0.000000000000001, 0.000000000065930, 0.000000597017644, 0.000585859662884, 0.062301883958987, 0.717975976728287, 0.896643486507500, 0.121347500208757, 0.001779684515109, 0.000002828501156, 0.000000000487159},
    {0.000000000000000, 0.000000000000001, 0.000000000065930, 0.000000382796005, 0.000240854107924, 0.016422598310807, 0.121347500208756, 0.097167482167606, 0.008431643111764, 0.000079287483413, 0.000000080797552},
    {0.000000000000000, 0.000000000000000, 0.000000000000001, 0.000000000027105, 0.000000100903931, 0.000040707551309, 0.001779684515109, 0.008431643111764, 0.004328949915153, 0.000240854107924, 0.000001452200915}
})

local nonStandardGaussianLogPDFWindow = torch.Tensor({
    -13.4424302802005, -16.3313191690894, -21.4424302802005, -28.7757636135338,
    -38.3313191690894, -50.1090969468671, -64.1090969468671, -80.3313191690893,
    -98.7757636135338, -119.4424302802, -142.331319169089, -8.33131916908937,
    -9.44243028020048, -12.7757636135338, -18.3313191690894, -26.1090969468671,
    -36.1090969468671, -48.3313191690894, -62.7757636135338, -79.4424302802005,
    -98.3313191690894, -119.4424302802, -5.44243028020048, -4.77576361353381,
    -6.33131916908937, -10.1090969468671, -16.1090969468671, -24.3313191690894,
    -34.7757636135338, -47.4424302802005, -62.3313191690893, -79.4424302802005,
    -98.7757636135338, -4.77576361353381, -2.33131916908936, -2.10909694686714,
    -4.10909694686714, -8.33131916908937, -14.7757636135338, -23.4424302802005,
    -34.3313191690894, -47.4424302802005, -62.7757636135338, -80.3313191690894,
    -6.33131916908936, -2.10909694686714, -0.109096946867141,
    -0.331319169089363, -2.77576361353381, -7.44243028020047,
    -14.3313191690894, -23.4424302802005, -34.7757636135338, -48.3313191690894,
    -64.1090969468671, -10.1090969468671, -4.10909694686714,
    -0.331319169089363, 1.22423638646619, 0.557569719799525, -2.33131916908936,
    -7.44243028020047, -14.7757636135338, -24.3313191690894, -36.1090969468671,
    -50.1090969468671, -16.1090969468671, -8.33131916908937, -2.77576361353381,
    0.557569719799526, 1.66868083091064, 0.557569719799525, -2.77576361353381,
    -8.33131916908936, -16.1090969468671, -26.1090969468671, -38.3313191690894,
    -24.3313191690894, -14.7757636135338, -7.44243028020047, -2.33131916908936,
    0.557569719799527, 1.22423638646619, -0.331319169089364, -4.10909694686714,
    -10.1090969468671, -18.3313191690894, -28.7757636135338, -34.7757636135338,
    -23.4424302802005, -14.3313191690894, -7.44243028020047, -2.77576361353381,
    -0.331319169089364, -0.109096946867142, -2.10909694686714,
    -6.33131916908936, -12.7757636135338, -21.4424302802005, -47.4424302802005,
    -34.3313191690894, -23.4424302802005, -14.7757636135338, -8.33131916908936,
    -4.10909694686714, -2.10909694686714, -2.33131916908936, -4.77576361353381,
    -9.44243028020047, -16.3313191690894, -62.3313191690893, -47.4424302802005,
    -34.7757636135338, -24.3313191690894, -16.1090969468671, -10.1090969468671,
    -6.33131916908937, -4.77576361353381, -5.44243028020048, -8.33131916908936,
    -13.4424302802005}):resize(11, 11)
    
function myTests.multivariateGaussianPDF()

    -- Standard 2-d gaussian, singleton samples, no result tensor
    local D = 2
    local N = 11

    -- Points at which to evaluate the PDF
    local inputXs = torch.linspace(-1, 1, N)
    local result = torch.Tensor(N, N)
    local mu = torch.Tensor(D):fill(0)
    local sigma = torch.eye(D, D)

    local returnNumbers = true
    local expected = standardGaussianPDFWindow
    for i = 1, N do
        for j = 1, N do
            local x = torch.Tensor({inputXs[i], inputXs[j]}) -- One point
            local r = distributions.mvn.pdf(x, mu, sigma)
            returnNumbers = returnNumbers and type(r) == 'number'
            result[i][j] = r
        end
    end
    tester:assert(returnNumbers, "should return a number when called with vectors only")
    tester:assertTensorEq(result, expected, 1e-15, "standard 2D gaussian pdf should match expected value")
end

function myTests.multivariateGaussianPDFNonStandard()

    -- Try calling D, D, D-D
    -- Non-standard 2-d gaussian, singleton samples, no result tensor
    local D = 2
    local N = 11

    -- Points at which to evaluate the PDF
    local inputXs = torch.linspace(-1, 1, N)
    local result = torch.Tensor(N, N)
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local expected = nonStandardGaussianPDFWindow

    local oldMu = mu:clone()
    local oldSigma = sigma:clone()

    local returnNumbers = true
    for i = 1, N do
        for j = 1, N do
            local x = torch.Tensor({inputXs[i], inputXs[j]}) -- One point
            local r = distributions.mvn.pdf(x, mu, sigma)
            returnNumbers = returnNumbers and type(r) == 'number'
            result[i][j] = r
        end
    end
    tester:assertTensorEq(mu, oldMu, 1e-14, "multivariateGaussianPDF should not modify sigma")
    tester:assertTensorEq(sigma, oldSigma, 1e-14, "multivariateGaussianPDF should not modify sigma")
    tester:assert(returnNumbers, "should return a number when called with vectors only")
    tester:assertTensorEq(result, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling NxD, D, DxD
function myTests.multivariateGaussianPDFMultiple1()

    -- Standard 2-d gaussian, multiple samples, no result tensor
    local D = 2
    local N = 11

    -- Points at which to evaluate the PDF
    local inputXs = torch.linspace(-1, 1, N)
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local x = torch.Tensor(N*N, D)
    local expected = torch.Tensor(N*N, 1)
    for i = 1, N do
        for j = 1, N do
            x[(i-1)*N+j][1] = inputXs[i]
            x[(i-1)*N+j][2] = inputXs[j]
            expected[(i-1)*N+j] = nonStandardGaussianPDFWindow[i][j]
        end
    end

    tester:assertTensorEq(distributions.mvn.pdf(x, mu, sigma), expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling OnexD, D, DxD
function myTests.multivariateGaussianPDFMultiple2()
    local x = torch.Tensor({{0, 0}})
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})
    local expected = torch.Tensor({{nonStandardGaussianPDFWindow[6][6]}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(distributions.mvn.pdf(x, mu, sigma), got, 1e-14, "multivariateGaussianPDF should not modify args")
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling D, OnexD, DxD
function myTests.multivariateGaussianPDFMultiple3()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})
    local expected = torch.Tensor({{nonStandardGaussianPDFWindow[6][6]}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling D, NxD, DxD
function myTests.multivariateGaussianPDFMultiple4()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}, {-0.4, 0.4}, {0.0, 0.0}})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})
    local expected = torch.Tensor({{nonStandardGaussianPDFWindow[6][6]}, {0.000000597017644}, {5.305164769729846}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Now with diagonal covariance only
-- Try calling D, D, D
function myTests.multivariateGaussianPDFMultiple5()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})
    local expected = 0.717583785682725
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertalmosteq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling D, 1-D, D
function myTests.multivariateGaussianPDFMultiple6()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}})
    local sigma = torch.Tensor({0.05, 0.4})
    local expected = torch.Tensor({{0.717583785682725}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling D, NxD, D
function myTests.multivariateGaussianPDFMultiple7()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}, {-0.4, 0.4}, {0.0, 0.0}})
    local sigma = torch.Tensor({0.05, 0.4})
    local expected = torch.Tensor({{0.717583785682725}, {0.186026607635655}, {1.125395395196383}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling OnexD, D, D
function myTests.multivariateGaussianPDFMultiple8()
    local x = torch.Tensor({{0, 0}})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})
    local expected = torch.Tensor({{0.717583785682725}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Try calling NxD, D, D
function myTests.multivariateGaussianPDFMultiple9()
    local x = torch.Tensor({{0, 0}, {0.1, 0.2}, {-0.3, -0.1}})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})
    local expected = torch.Tensor({{0.717583785682725}, {0.457551622898630}, {0.909950056726693}})
    local got = distributions.mvn.pdf(x, mu, sigma)
    tester:assertTensorEq(got, expected, 1e-14, "non-standard 2D gaussian pdf should match expected value")
end

-- Make sure that the inputs are not modified

-- Try calling NxD, D, DxD
function myTests.multivariateGaussianPDFSideEffects1()

    -- Standard 2-d gaussian, multiple samples, no result tensor
    local D = 2
    local N = 11

    -- Points at which to evaluate the PDF
    local inputXs = torch.linspace(-1, 1, N)
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local x = torch.Tensor(N*N, D)
    for i = 1, N do
        for j = 1, N do
            x[(i-1)*N+j][1] = inputXs[i]
            x[(i-1)*N+j][2] = inputXs[j]
        end
    end

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling OnexD, D, DxD
function myTests.multivariateGaussianPDFSideEffects2()
    local x = torch.Tensor({{0, 0}})
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling D, OnexD, DxD
function myTests.multivariateGaussianPDFSideEffects3()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling D, NxD, DxD
function myTests.multivariateGaussianPDFSideEffects4()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}, {-0.4, 0.4}, {0.0, 0.0}})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Now with diagonal covariance only
-- Try calling D, D, D
function myTests.multivariateGaussianPDFSideEffects5()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling D, 1-D, D
function myTests.multivariateGaussianPDFSideEffects6()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}})
    local sigma = torch.Tensor({0.05, 0.4})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling D, NxD, D
function myTests.multivariateGaussianPDFSideEffects7()
    local x = torch.Tensor({0, 0})
    local mu = torch.Tensor({{-0.2, 0.2}, {-0.4, 0.4}, {0.0, 0.0}})
    local sigma = torch.Tensor({0.05, 0.4})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling OnexD, D, D
function myTests.multivariateGaussianPDFSideEffects8()
    local x = torch.Tensor({{0, 0}})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Try calling NxD, D, D
function myTests.multivariateGaussianPDFSideEffects9()
    local x = torch.Tensor({{0, 0}, {0.1, 0.2}, {-0.3, -0.1}})
    local mu = torch.Tensor({-0.2, 0.2})
    local sigma = torch.Tensor({0.05, 0.4})

    local x2 = x:clone()
    local mu2 = mu:clone()
    local sigma2 = sigma:clone()

    local got = distributions.mvn.pdf(x, mu, sigma)

    tester:assertTensorEq(x, x2, 0, "x should not be modified")
    tester:assertTensorEq(mu, mu2, 0, "mu should not be modified")
    tester:assertTensorEq(sigma, sigma2, 0, "sigma should not be modified")
end

-- Same with result as first element
-- TODO

function myTests.multivariateGaussianLogPDFNonStandard()

    -- Try calling D, D, D-D
    -- Non-standard 2-d gaussian, singleton samples, no result tensor
    local D = 2
    local N = 11

    -- Points at which to evaluate the PDF
    local inputXs = torch.linspace(-1, 1, N)
    local result = torch.Tensor(N, N)
    local mu = torch.Tensor({0.2, -0.2})
    local sigma = torch.Tensor({{0.05, 0.04}, {0.04, 0.05}})

    local expected = nonStandardGaussianLogPDFWindow

    local returnNumbers = true
    for i = 1, N do
        for j = 1, N do
            local x = torch.Tensor({inputXs[i], inputXs[j]}) -- One point
            local r = distributions.mvn.logpdf(x, mu, sigma)
            returnNumbers = returnNumbers and type(r) == 'number'
            result[i][j] = r
        end
    end
    tester:assert(returnNumbers, "should return a number when called with vectors only")
    tester:assertTensorEq(result, expected, 1e-12, "non-standard 2D gaussian log-pdf should match expected value")
end

local function statisticalTestMultivariateGaussian(samples, mu, sigma, shouldAccept)

    -- Part one: chi2 test projection onto each axis

    assert(samples:dim() == 2)
    local N = samples:size(1)
    local D = samples:size(2)

    if mu:dim() > 1 then
        mu = torch.Tensor(mu):resize(mu:numel())
    end
    assert(mu:size(1) == D)

    assert(sigma:dim() == 2)
    assert(sigma:size(1) == D)
    assert(sigma:size(2) == D)

    local rejectionCount = 0
    for k = 1, D do
        local projectedSamples = samples:select(2, k)

        -- Now, we expect the distribution of the projected samples to be mu[k], math.sqrt(sigma[k][k])
        local p, chi2 = distributions.chi2Gaussian(projectedSamples, mu[k], math.sqrt(sigma[k][k]))

        if p < sidakCorrection(alpha, D) then
            -- we're rejecting the null hypothesis, that the sample is normally distributed with the above params
            rejectionCount = rejectionCount + 1
            tester:assert(not shouldAccept, "projected sample should be accepted as gaussian with given parameters (1)")
        end
    end

    -- Part two: transform and chi2 test against standard normal dist'n

    mu = torch.Tensor(mu)
    local expandedMu = mu:resize(1, D):expand(N, D)
    local whitenedSamples = samples:clone() - expandedMu
    local chol = torch.potrf(sigma):triu()
    whitenedSamples = torch.gesv(whitenedSamples:t(), chol:t()):t()
    for k = 1, D do
        local projectedSamples = whitenedSamples:select(2, k)
        local p, chi2 = distributions.chi2Gaussian(projectedSamples, 0, 1)
        if p < sidakCorrection(alpha, D) then
            rejectionCount = rejectionCount + 1
            tester:assert(not shouldAccept, "projected sample should be accepted as gaussian with given parameters (2)")
        end
    end

    -- If we're not supposed to be accepting this sample, check that it was rejected by at least one of the tests
    tester:assert(shouldAccept or rejectionCount > 0, "projected sample should be rejected as gaussian with given parameters")

end



-- D, DxD
function myTests.test_multivariateGaussianRand_D_DD()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.eye(2)
    local N = 10000
    local D = 2

    local dimOK = true
    local sizeOK = true
    local result = torch.Tensor(N, D):zero()
    for k = 1, N do
        local sample = distributions.mvn.rnd(mu, sigma)
        dimOK = dimOK and sample:dim() == 1
        sizeOK = sizeOK and sample:size(1) == D
        result[k] = sample
    end
    tester:assert(dimOK, "single sample should return vector result")
    tester:assert(sizeOK, "result should have size = 2")

    statisticalTestMultivariateGaussian(result, mu, sigma, true)
end

function myTests.test_multivariateGaussianRand_D_DD_errorSizes()
    -- Check we get an error with inconsistent sizes
    local mu = torch.zeros(3)
    local sigma = torch.eye(2) * 2
    tester:assertError(function() distributions.mvn.rnd(mu, sigma) end)
end


-- N, D, DxD
function myTests.multivariateGaussianRand_N_D_DD_Standard()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.eye(2)
    local N = 10000
    local D = 2

    local result = distributions.mvn.rnd(N, mu, sigma)
    tester:assert(result:dim() == 2, "multiple samples should return NxD tensor")
    tester:assert(result:size(1) == N, "multiple samples should return NxD tensor")
    tester:assert(result:size(2) == D, "multiple samples should return NxD tensor")
    statisticalTestMultivariateGaussian(result, mu, sigma, true)
end
function myTests.multivariateGaussianRand_N_D_DD()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.Tensor({{2.5, 0.1}, {0.1, 2.5}})
    local N = 20000
    local D = 2

    local result = distributions.mvn.rnd(N, mu, sigma)
    tester:assert(result:dim() == 2, "multiple samples should return NxD tensor")
    tester:assert(result:size(1) == N, "multiple samples should return NxD tensor")
    tester:assert(result:size(2) == D, "multiple samples should return NxD tensor")
    statisticalTestMultivariateGaussian(result, mu, sigma, true)
end
function myTests.multivariateGaussianRand_N_D_DD_fail_mean()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.eye(2)
    local N = 10000
    local D = 2

    local result = distributions.mvn.rnd(N, mu, sigma)

    -- Check we reject a sample with wrong mean
    result:select(2, 1):add(1)
    statisticalTestMultivariateGaussian(result, mu, sigma, false)
end

-- Check we reject a sample with wrong variance
function myTests.multivariateGaussianRand_N_D_DD_fail_variance()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.eye(2)
    local N = 10000
    local D = 2

    local result = distributions.mvn.rnd(N, mu, sigma)
    result:select(2, 1):mul(2)
    statisticalTestMultivariateGaussian(result, mu, sigma, false)
end
--
-- ResultTensor, D, DxD
function myTests.multivariateGaussianRand_Result_D_DD_Standard()
    local mu = torch.Tensor({10, 0})
    local sigma = torch.eye(2)
    local N = 10000
    local D = 2
    local result = torch.Tensor(N, D)

    distributions.mvn.rnd(result, mu, sigma)
    tester:assert(result:dim() == 2, "multiple samples should return NxD tensor")
    tester:assert(result:size(1) == N, "multiple samples should return NxD tensor")
    tester:assert(result:size(2) == D, "multiple samples should return NxD tensor")
    statisticalTestMultivariateGaussian(result, mu, sigma, true)
end

function myTests.testMultivariateDegenerateWithGP()
    -- One of the most useful use cases for a near-singular covariance
    -- matrix is a Gaussian process evaluated at very close points.
    -- In particular, the high dimension is very gooda at spotting
    -- errors in the use of the SVD.

    -- Number of points in the process
    local D = 500
    local x = torch.linspace(-10, 10, D)
    local mean = torch.zeros(D)
    local cov = torch.zeros(D, D)
    local sigma = 1.6
    for i = 1, D do
        for j = 1, D do
            local d = x[i] - x[j]
            cov[i][j] = math.exp(- math.pow(d, 2) / (2*sigma*sigma))
        end
    end

    local N = 10000
    local y = distributions.mvn.rnd(N, mean, cov)

    -- Statistical test on the sum of each trajectory sampled from the GP
    -- The sums should be distributed iid N(0, cov:sum()).
    -- If we mess up the transpose in the SVD, we will see a much smaller variance.
    local sums = y:sum(2)
    local p, chi2 = distributions.chi2Gaussian(sums, mean:sum(), math.sqrt(cov:sum()))
    tester:assert(p >= alpha,
                  'sums of GP trajectories with a close-to-singular matrix do not'
                  .. ' have the right distribution. Did you forget a transpose'
                  .. ' when using the SVD?')

end
-- NxD, D
-- D, NxD
-- NxD, NxD
-- N, D, D

function myTests.testMultivariateDegenerate()
    local N = 6
    local D = 3

    local mu = torch.rand(1,  D)
    local mean = mu:expand(N, D)
    local cov = torch.eye(D)
    cov[D][D] = 0

    local actual = torch.Tensor(N, D)
    distributions.mvn.rnd(actual, mean, cov)
    -- Check that the second column is constant
    tester:assertTensorEq(actual:select(2,D), mean:select(2,D), 1e-16, 'did not generate constant values')
end

function myTests.testCholesky()
    local N = 30
    local D = 2

    local options = {cholesky = true}

    local mu = torch.Tensor{1, 2}
    local cov = torch.Tensor{{3, 2}, {2, 4}}

    local state = torch.getRNGState()
    local xFull = distributions.mvn.rnd(N, mu, cov)
    torch.setRNGState(state)
    local xChol = distributions.mvn.rnd(N, mu, torch.potrf(cov):triu(), options)
    tester:assertTensorEq(xChol, xFull, 1e-16, 'Rnd with and without full cholesky should generate same values')

    local state = torch.getRNGState()
    local diag = torch.diag(cov)
    local xFull = distributions.mvn.rnd(N, mu, diag)
    torch.setRNGState(state)
    local xChol = distributions.mvn.rnd(N, mu, diag:clone():sqrt(), options)
    tester:assertTensorEq(xChol, xFull, 1e-16, 'Rnd with and without diag cholesky should generate same values')

    local x = torch.randn(N, D)
    local logpdfFull = distributions.mvn.logpdf(x, mu, cov)
    local logpdfChol = distributions.mvn.logpdf(x, mu, torch.potrf(cov):triu(), options)
    tester:assertTensorEq(logpdfChol, logpdfFull, 1e-16, 'Logpdf with and without full cholesky should return same result')

    local x = torch.randn(N, D)
    local logpdfFull = distributions.mvn.logpdf(x, mu, torch.diag(cov))
    local logpdfChol = distributions.mvn.logpdf(x, mu, torch.diag(cov):sqrt(), options)
    tester:assertTensorEq(logpdfChol, logpdfFull, 1e-16, 'Logpdf with and without diag cholesky should return same result')

    local x = torch.randn(N, D)
    local pdfFull = distributions.mvn.pdf(x, mu, cov)
    local pdfChol = distributions.mvn.pdf(x, mu, torch.potrf(cov):triu(), options)
    tester:assertTensorEq(pdfChol, pdfFull, 1e-16, 'pdf with and without full cholesky should return same result')

    local x = torch.randn(N, D)
    local pdfFull = distributions.mvn.pdf(x, mu, torch.diag(cov))
    local pdfChol = distributions.mvn.pdf(x, mu, torch.diag(cov):sqrt(), options)
    tester:assertTensorEq(pdfChol, pdfFull, 1e-16, 'pdf with and without diag cholesky should return same result')

end

local function generateSystematicTests()
    local N = 10000
    local M = 3
    local D = 2

    local firstArgOptions = { N = N, M = M, NxD = torch.Tensor(N, D) }

    local secondArgD = torch.Tensor { 10, 0 }
    local secondArg1D = torch.Tensor {{ 11, 0 }}
    local secondArgMD = torch.Tensor(M, D):zero()
    local k = 0
    secondArgMD:apply(function()
        k = k + 1
        return k % 2 * ((k - 1) / 2)
    end)
    local secondArgE = torch.Tensor { 10, 0, 0 }

    local secondArgOptions = { D = secondArgD, OnexD = secondArg1D, E = secondArgE, MxD = secondArgMD }

    local thirdArgD = torch.Tensor { 2, 1 }
    local thirdArgDD = torch.Tensor {{2, 1}, {1, 1}}
    local thirdArgMDD = torch.Tensor(M, D, D):zero()
    for k = 1, M do
        thirdArgMDD[k] = torch.Tensor {{k+1, k}, {k, k}}
    end
    local thirdArgDE = torch.Tensor {{2, 1, 1}, {1, 1, 1}}
    local thirdArgEE = torch.Tensor {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}

    local thirdArgOptions = { D = thirdArgD, DxD = thirdArgDD, DxE = thirdArgDE, ExE = thirdArgEE, MxDxD = thirdArgMDD }

    local function shouldError(v1, v2, v3, desc)
        tester:assertError(
                function() distributions.mvn.rnd(v1, v2, v3) end,
                desc .. " should error!"
            )
    end

    local function checkResultsGaussian(result, mu, sigma)
        tester:assert(result, "got no result - expected samples from a gaussian!")
        tester:assert(result:dim(), 2, "wrong dimensionality for result")
        tester:asserteq(result:size(2), mu:numel(), "expected results with " .. mu:numel() .. "columns, got " .. result:size(2) .. " instead")
        statisticalTestMultivariateGaussian(result, mu, sigma, true)
    end

    local function shouldBeFromOneGaussian(v1, v2, v3, desc)
        local result = distributions.mvn.rnd(v1, v2, v3)
        checkResultsGaussian(result, v2, v3)
    end

    local function shouldBeFromOneDiagonalGaussian(v1, v2, v3, desc)
        local result = distributions.mvn.rnd(v1, v2, v3)
        checkResultsGaussian(result, v2, torch.diag(v3))
    end

    local function shouldBeFromMGaussians(v1, v2, v3, desc)

        local accumulated = torch.Tensor(M, N, D):zero()

        -- Each call only returns one sample from each distribution, so to
        -- perform our statistical tests we need to make many calls.
        local notNil = true
        local correctDim = true
        local correctSize = true
        for k = 1, N do
            local results = distributions.mvn.rnd(v1, v2, v3)
            notNil = notNil and results ~= nil
            correctDim = correctDim and results:dim() == 2
            correctSize = correctSize and results:size(1) == M
            local gaussDim
            if v2:dim() == 2 then
                gaussDim = v2:size(2)
            else
                gaussDim = v2:size(1)
            end
            correctSize = correctSize and results:size(2) == gaussDim
            for j = 1, M do
                accumulated[j][k] = results[j]
            end
        end

        tester:assert(notNil, "got no result - expected samples from a gaussian!")
        tester:assert(correctDim, "wrong dimensionality for result")
        tester:assert(correctSize, "expected results of correct size")

        for j = 1, M do
            local mu = v2
            if v2:dim() == 2 and v2:size(1) ~= 1 then
                mu = v2[j]
            end
            local sigma = v3
            if v3:dim() == 3 then
                sigma = v3[j]
            end
            statisticalTestMultivariateGaussian(accumulated[j], mu, sigma, true)
        end
    end

    local function null() end

    local expectations = {}
    expectations["N, D, D"] = shouldBeFromOneDiagonalGaussian
    expectations["N, D, DxD"] = shouldBeFromOneGaussian
    expectations["N, D, DxE"] = shouldError
    expectations["N, D, ExE"] = shouldError
    expectations["N, D, MxDxD"] = shouldError

    expectations["N, OnexD, D"] = shouldBeFromOneDiagonalGaussian
    expectations["N, OnexD, DxD"] = shouldBeFromOneGaussian
    expectations["N, OnexD, DxE"] = shouldError
    expectations["N, OnexD, ExE"] = shouldError
    expectations["N, OnexD, MxDxD"] = shouldError

    expectations["N, E, D"] = shouldError
    expectations["N, E, DxD"] = shouldError
    expectations["N, E, DxE"] = shouldError
    expectations["N, E, ExE"] = shouldBeFromOneGaussian
    expectations["N, E, MxDxD"] = shouldError

    expectations["N, MxD, D"] = shouldError
    expectations["N, MxD, DxD"] = shouldError
    expectations["N, MxD, DxE"] = shouldError
    expectations["N, MxD, ExE"] = shouldError
    expectations["N, MxD, MxDxD"] = shouldError

    expectations["M, D, D"] = null
    expectations["M, D, DxD"] = null
    expectations["M, D, DxE"] = shouldError
    expectations["M, D, ExE"] = shouldError
    expectations["M, D, MxDxD"] = shouldBeFromMGaussians

    expectations["M, OnexD, D"] = null
    expectations["M, OnexD, DxD"] = null
    expectations["M, OnexD, DxE"] = shouldError
    expectations["M, OnexD, ExE"] = shouldError
    expectations["M, OnexD, MxDxD"] = shouldBeFromMGaussians

    expectations["M, E, D"] = null
    expectations["M, E, DxD"] = null
    expectations["M, E, DxE"] = shouldError
    expectations["M, E, ExE"] = null
    expectations["M, E, MxDxD"] = shouldError

    expectations["M, MxD, D"] = null
    expectations["M, MxD, DxD"] = shouldBeFromMGaussians
    expectations["M, MxD, DxE"] = shouldError
    expectations["M, MxD, ExE"] = shouldError
    expectations["M, MxD, MxDxD"] = shouldBeFromMGaussians

    expectations["NxD, D, D"] = shouldBeFromOneDiagonalGaussian
    expectations["NxD, D, DxD"] = shouldBeFromOneGaussian
    expectations["NxD, D, DxE"] = shouldError
    expectations["NxD, D, ExE"] = shouldError
    expectations["NxD, D, MxDxD"] = shouldError

    expectations["NxD, OnexD, D"] = shouldBeFromOneDiagonalGaussian
    expectations["NxD, OnexD, DxD"] = shouldBeFromOneGaussian
    expectations["NxD, OnexD, DxE"] = shouldError
    expectations["NxD, OnexD, ExE"] = shouldError
    expectations["NxD, OnexD, MxDxD"] = shouldError

    expectations["NxD, E, D"] = shouldError
    expectations["NxD, E, DxD"] = shouldError
    expectations["NxD, E, DxE"] = shouldError
    expectations["NxD, E, ExE"] = shouldError -- TODO: check with @d11 why it was not error
    expectations["NxD, E, MxDxD"] = shouldError

    expectations["NxD, MxD, D"] = null
    expectations["NxD, MxD, DxD"] = shouldError -- TODO: check with @d11 why it was not error
    expectations["NxD, MxD, DxE"] = shouldError
    expectations["NxD, MxD, ExE"] = shouldError
    expectations["NxD, MxD, MxDxD"] = shouldError -- tODO: check with @d11 why it was not error

    local testTable = {}

    for i1, v1 in pairs(firstArgOptions) do
        for i2, v2 in pairs(secondArgOptions) do
            for i3, v3 in pairs(thirdArgOptions) do
                local key = table.concat { i1, ", ", i2, ", ", i3 }
                local desc = table.concat { "distributions.mvn.rnd(", key, ")" }
                local testFunc = expectations[key]
                if not testFunc then
                    error("Missing expected result handler for " .. desc)
                end
                testTable["test_multivariateGaussianRand_" .. string.gsub(key, ", ", "_")] = function()
--[[                print('\nrunning', desc)
                    print('i1', i1)
                    print('v1', v1)
                    print('i2', i2)
                    print('v2', v2)
                    print('i3', i3)
                    print('v3', v3) ]]
                    local x1
                    if type(v1) == 'number' then
                        x1 = v1
                    else
                        x1 = v1:clone()
                    end
                    testFunc(x1, v2:clone(), v3:clone(), desc)
              end
            end
        end
    end
    return testTable
end

function myTests.test1D1D()
    local D = 10
    local x = distributions.mvn.rnd(torch.zeros(1,D), torch.ones(1,D), {cholesky = true})
end


function myTests.testResize()
    local N, D =  2, 10
    local call = {
        mu = torch.zeros(D),
        x = torch.randn(N, D),
        cov = torch.ones(D)
    }
    local ori = {}
    for k,v in pairs(call) do
        ori[k] = v:clone()
    end

    local l = distributions.mvn.logpdf(call.x, call.mu, call.cov)
    for k,v in pairs(call) do
        tester:asserteq(call[k]:dim(), ori[k]:dim(),'Call changed dim of param ' .. k)
        if call[k]:dim() == ori[k]:dim() then
            for i=1, call[k]:dim() do
                tester:asserteq(call[k]:size(i), ori[k]:size(i),'Call changed size of param ' .. k)
            end
        end
    end
end

function myTests.testMultivariateGaussianEntropy()
    local sigma = torch.randn(10,10)
    sigma = sigma * sigma:t()
    tester:assert(distributions.mvn.entropy(sigma))
end

function myTests.testMultivariateGaussianKL()
    local p = {
        mu = torch.randn(10),
        sigma = torch.randn(10,10)
    }
    p.sigma = p.sigma * p.sigma:t()

    local q = {
        mu = torch.randn(10),
        sigma = torch.randn(10,10)
    }
    q.sigma = q.sigma * q.sigma:t()

    tester:assert(distributions.mvn.kl(p,q) >= 0)
    tester:assert(distributions.mvn.kl(q,p) >= 0)
    tester:assertalmosteq(distributions.mvn.kl(p,p), 0, 1e-12)
    tester:assertalmosteq(distributions.mvn.kl(q,q), 0, 1e-12)
end

tester:add(myTests)
--tester:add(generateSystematicTests())
return tester:run()
