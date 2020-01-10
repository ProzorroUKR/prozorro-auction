var auction_doc_id = 'test';
beforeEach(module('auction'));

describe('Unit: Testing Filter "formatnumber" - ', function() {
  it('formatnumber should format positive numbers', inject(function($filter) {
    expect($filter('formatnumber')(100000)).toEqual('100 000');
    expect($filter('formatnumber')(10000)).toEqual('10 000');
    expect($filter('formatnumber')(1000)).toEqual('1 000');
    expect($filter('formatnumber')(100)).toEqual('100');
    expect($filter('formatnumber')(10)).toEqual('10');
    expect($filter('formatnumber')(1)).toEqual('1');
  }));

  it('formatnumber should format nagative numbers', inject(function($filter) {
    expect($filter('formatnumber')(-100000)).toEqual('-100 000');
    expect($filter('formatnumber')(-10000)).toEqual('-10 000');
    expect($filter('formatnumber')(-1000)).toEqual('-1 000');
    expect($filter('formatnumber')(-100)).toEqual('-100');
    expect($filter('formatnumber')(-10)).toEqual('-10');
    expect($filter('formatnumber')(-1)).toEqual('-1');
  }));

  it('formatnumber should works with incorect values', inject(function($filter) {
    expect($filter('formatnumber')('string')).toEqual('');
    expect($filter('formatnumber')('')).toEqual($filter('number')('')); // '0' 
    expect($filter('formatnumber')({})).toEqual('');
    expect($filter('formatnumber')(true)).toEqual('');
    expect($filter('formatnumber')(false)).toEqual('');
  }));
});



describe('Unit Testing: Filter "fraction" - ', function() {
  it('floor should cut to the given precision', inject(function($filter) {
    expect($filter('fraction')(8546.998)).toEqual('8 547,00');
    expect($filter('fraction')(8547)).toEqual('8 547,00');

    expect($filter('fraction')("2")).toEqual('2,00');
    expect($filter('fraction')("2000.3")).toEqual('2 000,30');
    expect($filter('fraction')("1/8")).toEqual('0,13');
    expect($filter('fraction')("0.(3)")).toEqual('0,33');
    expect($filter('fraction')(undefined)).toEqual('');
    expect($filter('fraction')(true)).toEqual('1,00');
    expect($filter('fraction')(false)).toEqual('0,00');
  }));
});

describe('Unit Testing: Filter "floor" - ', function() {
  it('floor should cut to the given precision', inject(function($filter) {
    expect($filter('floor')(8546.99876, 4)).toEqual('8 546,9987');
    expect($filter('floor')(8546.998, 3)).toEqual('8 546,998');
    expect($filter('floor')(8546.998, 2)).toEqual('8 546,99');
    expect($filter('floor')(8546.998, 1)).toEqual('8 546,9');
    expect($filter('floor')(8546.998, 0)).toEqual('8 546');
    expect($filter('floor')(8546.998)).toEqual('8 546');

    expect($filter('floor')("2", 2)).toEqual('2,00');
    expect($filter('floor')("2000.3", 2)).toEqual('2 000,30');
    expect($filter('floor')("1/8", 2)).toEqual('0,12');
    expect($filter('floor')("1/8", 3)).toEqual('0,125');
    expect($filter('floor')("0.(3)", 2)).toEqual('0,33');
    expect($filter('floor')("0.(3)", 5)).toEqual('0,33333');
    expect($filter('floor')("0.(3)")).toEqual('0');
    expect($filter('floor')(undefined, 2)).toEqual('');
    expect($filter('floor')(true, 2)).toEqual('1,00');
    expect($filter('floor')(false, 2)).toEqual('0,00');
  }));
});