require 'totem'
require 'distributions'

local mytest = {}
local tester = totem.Tester()

function mytest.testChiSquareGaussian()
    local nPoints = 1000
    local mu = 5
    local sigma = 10
    local x = torch.randn(nPoints)
    x = x * sigma + mu
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2Gaussian(x, mu, sigma)
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p > 0.001, 'Chi-square test rejects a sample from a gaussian distribution')
    x = x + 10
    local p, chi2 = distributions.chi2Gaussian(x, mu, sigma)
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a wrong sample from a gaussian distribution')
end

function mytest.testChiSquareUniformAccept()
    local nPoints = 1000
    local x = torch.Tensor(nPoints)
    local low = -10
    local up = 10
    for i=1,nPoints do
        x[i] = torch.uniform(low, up)
    end
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2Uniform(x, low, up)
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p > 0.001, 'Chi-square test rejects a sample from a uniform distribution')
end

function mytest.testChiSquareUniformRejectWithinSupport()
    local nPoints = 5000
    local x = torch.Tensor(nPoints)
    local low = -10
    local up = 10
    for i=1,nPoints do
        x[i] = torch.uniform(0, up)
    end
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2Uniform(x, low, up)
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a sample from a wrong uniform distribution within support')
end

function mytest.testChiSquareUniformRejectOutOfSupport()
    local nPoints = 1000
    local x = torch.Tensor(nPoints)
    for i=1,nPoints do
        x[i] = torch.uniform(100, 110)
    end
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2Uniform(x, 0, 10)
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a sample from a wrong uniform distribution out of support')
    tester:assert(chi2 == math.huge, 'Chi-square with out of support does not return infinite test statistic')
end

function mytest.testChiSquareCDF()

    local low = -6
    local up = -4

    -- Uniform distribution (vectorised)
    local function cdf(xs)
        for k = 1,xs:size(1) do
            local x = xs[k]
            if x < low or x > up then
                xs[k] = 0
            else
                xs[k] = (x - low) / (up - low)
            end
        end
        return xs
    end

    local nPoints = 1000
    local x = torch.Tensor(nPoints)
    for i=1,nPoints do
        x[i] = torch.uniform(low, up)
    end
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2TestCDF(x, cdf, {})
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p > 0.001, 'Chi-square test rejects a sample from a uniform distribution')

    for i=1,nPoints do
        x[i] = torch.uniform(low, (low + up) / 2)
    end
    -- Chi-square test at 99.9%
    local p, chi2 = distributions.chi2TestCDF(x, cdf, {})
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a sample from a uniform distribution with a smaller support')
    tester:assert(chi2, 'Test statistic should not be nil')

    for i=1,nPoints do
        x[i] = torch.uniform(low - 10, up + 10)
    end
    -- Chi-square test at 99.9%
    p, chi2 = distributions.chi2TestCDF(x, cdf, {})
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a sample from a uniform distribution with a larger support')

    for i=1,nPoints do
        x[i] = torch.uniform(low - 10, up - 10)
    end
    -- Chi-square test at 99.9%
    p, chi2 = distributions.chi2TestCDF(x, cdf, {})
    tester:assert(chi2, 'Test statistic should not be nil')
    tester:assert(p < 0.001, 'Chi-square test accepts a sample from a uniform distribution with non-intersecting support')

    -- Test invalid calls
    tester:assertError(function() distributions.chi2TestCDF() end, "chi2TestCDF should error when given no arguments")
    tester:assertError(function() distributions.chi2TestCDF(torch.Tensor()) end, "chi2TestCDF should error when given one argument")
    tester:assertError(function() distributions.chi2TestCDF(torch.Tensor(), function() end) end, "chi2TestCDF should error when given two arguments")
    tester:assertError(function() distributions.chi2TestCDF({}, function() end, {}) end, "chi2TestCDF should error when given incorrectly typed first argument")
    tester:assertError(function() distributions.chi2TestCDF(torch.Tensor(), {}, {}) end, "chi2TestCDF should error when given incorrectly typed second argument")
    tester:assertError(function() distributions.chi2TestCDF(torch.Tensor(), function() end, 3) end, "chi2TestCDF should error when given incorrectly typed third argument")
end

tester:add(mytest)
return tester:run()
