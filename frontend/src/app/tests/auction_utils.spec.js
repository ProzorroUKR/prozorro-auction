var auction_doc_id = 'test';

beforeEach(function() {
    module('auction')
    timerCallback = jasmine.createSpy("timerCallback");
    jasmine.clock().install();
  });

afterEach(function() {
    jasmine.clock().uninstall();
  });

angular.mock.module('auction');

describe('Unit: Testing AuctionUtils "pad" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.pad).toBeDefined();
  }]));

  it('should be convert 10 to "10"', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.pad(10)).toEqual("10");
  }]));

  it('should be convert 1 to "01"', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.pad(1)).toEqual("01");
  }]));
});


describe('Unit: Testing AuctionUtils "prepare_info_timer_data" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.prepare_info_timer_data).toBeDefined();
  }]));
});