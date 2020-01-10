//stringifyQueryString
describe('Unit: Testing AuctionUtils "stringifyQueryString" ', function() {

  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.stringifyQueryString).toBeDefined();
  }]));

  it('should return empty string if argument is undefined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.stringifyQueryString()).toEqual('');
  }]));

  it('should convert object', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.stringifyQueryString({a:1,b:2,c:3})).toEqual('a=1&b=2&c=3');
    expect(AuctionUtils.stringifyQueryString({a:1,b:2})).toEqual('a=1&b=2');
    expect(AuctionUtils.stringifyQueryString({a:1})).toEqual('a=1');
  }]));

  it('should convert object with arrays', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.stringifyQueryString({a:[1,2,3],c:[1,2,3]})).toEqual('a=1&a=2&a=3&c=1&c=2&c=3');
    expect(AuctionUtils.stringifyQueryString({a:[1,2],c:[1,2,3]})).toEqual('a=1&a=2&c=1&c=2&c=3');
    expect(AuctionUtils.stringifyQueryString({a:[1],c:[1,2,3]})).toEqual('a=1&c=1&c=2&c=3');
    expect(AuctionUtils.stringifyQueryString({a:[1],c:[1,2]})).toEqual('a=1&c=1&c=2');
    expect(AuctionUtils.stringifyQueryString({a:[1],c:[1]})).toEqual('a=1&c=1');
  }]));

  it('should encodeURI', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.stringifyQueryString({'a v':'http://w3schools.com/my test.asp?name=ståle&car=saab'}))
      .toEqual('a%20v=http%3A%2F%2Fw3schools.com%2Fmy%20test.asp%3Fname%3Dst%C3%A5le%26car%3Dsaab');
  }]));
});

//prepare_title_ending_data
describe('Unit: Testing AuctionUtils "prepare_title_ending_data" ', function() {

  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.prepare_title_ending_data).toBeDefined();
  }]));
});

//pad
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

//inIframe
describe('Unit: Testing AuctionUtils "inIframe" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.inIframe).toBeDefined();
  }]));

  it('should return', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    window.self = true;
    window.top = false;
    expect(AuctionUtils.inIframe()).toEqual(true);
  }]));
});

//polarToCartesian
describe('Unit: Testing AuctionUtils "polarToCartesian" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.polarToCartesian).toBeDefined();
  }]));

  it('should return correct result', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.polarToCartesian(10, 10, 10, 90)).toEqual({x: 20, y: 10});
    expect(AuctionUtils.polarToCartesian(10, 10, 10, 180)).toEqual({x: 10, y: 20});
    expect(AuctionUtils.polarToCartesian(1, 2, 10, 45)).toEqual({x: 8.071067811865476, y: -5.071067811865475});
  }]));
});

//generateUUID
describe('Unit: Testing AuctionUtils "generateUUID" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.generateUUID).toBeDefined();
  }]));

  it('should return correct result', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    var UUID = AuctionUtils.generateUUID();
    var someUUID = AuctionUtils.generateUUID();
    var regEx = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/;

    expect(UUID[14]).toEqual('4');
    expect(someUUID[14]).toEqual('4');
    expect(UUID.split('-').length).toEqual(5);
    expect(UUID.length).toEqual(36);
    expect(UUID).not.toEqual(someUUID);
    expect(regEx.test(UUID)).toEqual(true);
  }]));
});

//detectIE
describe('Unit: Testing AuctionUtils "detectIE" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.detectIE).toBeDefined();
  }]));
  
  it('should detect MSIE or Trident or Edge ', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    var ua = window.navigator.userAgent;
    var regEx = /MSIE|Trident|Edge/;
    expect(!!AuctionUtils.detectIE()).toEqual(regEx.test(ua));
  }]));
});

//UnsupportedBrowser
describe('Unit: Testing AuctionUtils "UnsupportedBrowser" ', function() {
  it('should be Defined', angular.mock.inject(['AuctionUtils', function(AuctionUtils) {
    expect(AuctionUtils.UnsupportedBrowser).toBeDefined();
  }]));
});