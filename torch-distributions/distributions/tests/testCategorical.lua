require 'torch'
require 'totem'
local dist = require('distributions')

local tester = totem.Tester()
local testCategorical = {}

function testCategorical.testCallNoResult()
    local x
    local p = torch.Tensor{.3, .3, .4}

    -- call with 1 parameter
    x = dist.cat.rnd(p)
    tester:asserteq(x:numel(), 1)

    -- calls with 2 parameters
    local N = 10
    x = dist.cat.rnd(N, p)
    tester:asserteq(x:numel(), N)

    local options = {type = 'stratified'}
    x = dist.cat.rnd(p, options)
    tester:asserteq(x:numel(), 1)

    -- call with 3 parameters
    x = dist.cat.rnd(N, p, options)
    tester:asserteq(x:numel(), N)
end

function testCategorical.testCallResult()
    local x
    local p = torch.Tensor{.3, .3, .4}

    -- calls with 2 parameters
    local res = torch.LongTensor(10):fill(0)
    x = dist.cat.rnd(res, p)
    tester:asserteq(x, res, '2 params did not use result tensor')

    -- calls with 2 parameters, not a LongTensor
    local res = torch.DoubleTensor(10):fill(0)
    x = dist.cat.rnd(res, p)
    tester:asserteq(x, res, '2 params with did not use result DoubleTensor')

    -- call with 3 parameters
    local options = {type = 'stratified'}
    x = dist.cat.rnd(res, p, options)
    tester:asserteq(x, res, '3 params did not use result tensor')
end

function testCategorical.testNormalization()
    local p = torch.Tensor({0,1})
    local x = dist.cat.rnd(10, p)
    for i=1, 10 do
        tester:asserteq(x[i], 2, 'should be all 2')
    end

    local nfreq = 10000
    local p10 = torch.Tensor({5, 5})
    local x = dist.cat.rnd(nfreq, p10)
    local freq={}
    for i = 1, nfreq do
        if not freq[x[i]] then freq[x[i]] = 0 end
        freq[x[i]] = freq[x[i]] + 1
    end
    tester:assert(freq[1] and freq[2], 'seems that we have a normalization problem')
end

function testCategorical.zeroprob()
    local nullProba = torch.zeros(10)
    tester:assertError(function() dist.cat.rnd(1, nullProba) end, 'should not be able to resample with null total mass')
end

function testCategorical.resampleCategories()
    local nrow = 30
    local ncol = 20
    local x = torch.zeros(nrow, ncol)
    for i = 1, nrow do
        x[i] = torch.range(10*i, 10*i+ncol):resize(1,ncol)
    end

    -- should throw an error when probabilities are not assigned to each row
    local p = torch.ones(nrow - 1)
    tester:assertError(function() dist.cat.rnd(p, {categories = x}) end, 'should require probabilities for each row')

    local onlySurvivor = 2
    local p = torch.zeros(nrow)
    local N = 10
    p[onlySurvivor] = 1
    local expected = torch.Tensor(N,ncol)
    for i = 1, N do
        expected[i] = x[onlySurvivor]
    end
    local res = dist.cat.rnd(N, p, {categories = x})
    tester:assertTensorEq(res, expected, 1e-16, 'should have only survivor')

    local nExtended = 50
    local expected = torch.Tensor(nExtended,ncol)
    for i = 1, nExtended do
        expected[i] = x[onlySurvivor]
    end
    tester:assertTensorEq(dist.cat.rnd(nExtended, p, {categories = x}), expected, 1e-16, 'should have extended survivor')

    local nShrinked = 2
    local expected = torch.Tensor(nShrinked,ncol)
    for i = 1, nShrinked do
        expected[i] = x[onlySurvivor]
    end
    tester:assertTensorEq(dist.cat.rnd(nShrinked, p, {categories = x}), expected, 1e-16, 'should have shrinked survivor')
end


local function isSamplerSorted(sampler)
    local p = torch.ones(10)
    local nSamples = 10000
    local x = dist.cat.rnd(nSamples, p, {type = sampler})
    local isSorted = true
    for i = 2,nSamples do
        if x[i] < x[i-1] then
            isSorted = false
        end
    end
    return isSorted
end

function testCategorical.testStratifiedIsSorted()
    tester:assert(isSamplerSorted('stratified') == true, 'Stratified indices should be sorted')
end

function testCategorical.testDichotomyIsNotSorted()
    tester:assert(isSamplerSorted('dichotomy') == false, 'Indices should NOT be sorted')
end

function testCategorical.testUnsortedIsNotSorted()
    tester:assert(isSamplerSorted('iid') == false, 'Indices should NOT be sorted')
end

local function assert_unbiased(sampler)
    local p = torch.ones(10)
    local nrep = 10000
    local countOne = 0
    for i = 1,nrep do
        local x = dist.cat.rnd(1, p, {type = sampler})
        if x[1] == 1 then
            countOne = countOne + 1
        end
    end
    -- TOOD: use Chisquare test instead
    -- Very crude hypothesis testing :p
    tester:assert(countOne < 3*nrep/10, 'Sampled 1 way too often')
end

function testCategorical.testUnsortedWithOneSample()
    assert_unbiased('iid')
end

function testCategorical.testDichotomyWithOneSample()
    assert_unbiased('dichotomy')
end

function testCategorical.testStratifiedWithOneSample()
    assert_unbiased('stratified')
end

function testCategorical.testMultivariate()
--[[
This would be a convenience method. If p is a NxM tensor, the result would be
to generate N independent samples from N categorical distributions. The i-th
sample would be obtained with probabilities given by the vector p[i].

Use case: sampling from the output of a neural network having a softmax output
layer. N in this case corresponds to the size of the minibatch. When used in
conjunction with torch.nn, this would allow for the following:
]]
    --- Without result tensor nor number of samples
    local p = torch.Tensor{{.1, .2, .7},{.9, 0, .1}}
    local x = dist.mvcat.rnd(p)
    tester:asserteq(x:dim(), 2, 'new result should be a matrix')
    tester:asserteq(x:size(1), p:size(1), 'Wrong number of rows for new result')
    tester:asserteq(x:size(2), 1, 'Wrong number of columns for new result')

    --- With number of samples
    local nSamples = 10000
    local x = dist.mvcat.rnd(nSamples, p)
    tester:asserteq(x:dim(), 2, 'new result should be a matrix')
    tester:asserteq(x:size(1), p:size(1), 'Wrong number of rows for new result')
    tester:asserteq(x:size(2), nSamples, 'Wrong number of columns for new result')


    --- With result tensor
    local result = torch.Tensor(2, nSamples)
    dist.mvcat.rnd(result, p)
    tester:asserteq(result:dim(), 2, 'result should be a matrix')
    tester:asserteq(result:size(1), p:size(1), 'Wrong number of rows for tensor result')
    tester:asserteq(result:size(2), nSamples, 'Wrong number of columns for tensor result')
end

tester:add(testCategorical)
return tester:run()
