describe('Post Bid Form Tests', function () {
  var controller, scope, rootScope;

  beforeEach(module('auction'));
  beforeEach(inject(function($injector, _$controller_, _$rootScope_, AuctionUtils){
    scope = _$rootScope_.$new();
    rootScope = _$rootScope_;
    controller = _$controller_('AuctionController', {$scope: scope, AuctionUtils: AuctionUtils, $rootScope: rootScope});
  }));

  beforeEach(inject(function($compile, $rootScope) {
    rootScope.form = {bid: null }
    rootScope.calculated_max_bid_amount = 1000;
    rootScope.minimal_bid = {amount: 100};
    rootScope.auction_doc = {
        current_stage: 1,
        stages: [
            {amount: 1100},
            {amount: 1000},
        ],
    };
    var element = angular.element(
      '<form id="BidsForm" name="form.BidsForm" role="form">' +
      '<input name="bid" ng-model="$root.form.bid" format>' +
      '</form>'
    );
    $compile(element)(rootScope);
  }));

  it('should raise validation error if bid is less than 70% of max allowed', function () {
      scope.form.BidsForm.bid.$setViewValue('100');
      scope.$digest();
      expect(scope.form.bid).toEqual("100");

      expect(scope.post_bid()).toBe(0);
      expect(scope.alerts.length).toBe(1);
      expect(scope.alerts[0].msg).toBe("You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?");
      expect(scope.alerts[0].msg_vars.too_low_bid_ratio).toEqual("90.00");
  });

  it('should raise validation error if bid is zero', function () {
      scope.form.BidsForm.bid.$setViewValue("0");
      scope.$digest();

      expect(scope.form.bid).toEqual("0");
      expect(scope.post_bid()).toBe(0);
      expect(scope.alerts.length).toBe(1);
      expect(scope.alerts[0].msg).toBe("You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?");
      expect(scope.alerts[0].msg_vars.too_low_bid_ratio).toEqual("100.00");
  });

  it('should not raise validation error while bid cancellation', function () {
      scope.form.BidsForm.bid.$setViewValue("900");
      scope.$digest();

      expect(scope.form.bid).toEqual("900");
      expect(scope.post_bid(-1)).toBe(undefined);
      expect(scope.alerts.length).toBe(0);
  });

  it('should not raise validation error while bid cancellation', function () {
      scope.form.BidsForm.bid.$setViewValue("10");
      scope.$digest();

      expect(scope.form.bid).toEqual("10");
      expect(scope.post_bid(-1)).toBe(undefined);
      expect(scope.alerts.length).toBe(0);
  });

  it('should not raise exception if bid is greater than 70% of max allowed', function () {
      scope.form.BidsForm.bid.$setViewValue('700.01');
      scope.$digest();
      expect(scope.form.bid).toEqual("700.01");
      expect(scope.post_bid()).toBe(undefined);
      expect(scope.alerts.length).toBe(0);
  });

  it('should disable validation once post_bid is called', function () {
      scope.form.BidsForm.bid.$setViewValue('700');
      scope.$digest();
      expect(scope.form.bid).toEqual("700");

      expect(scope.force_post_low_bid).toBe(undefined);
      expect(scope.post_bid()).toBe(0);
      expect(scope.alerts[0].msg).toBe("You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?");

      expect(scope.force_post_low_bid).toBe(700);
      expect(scope.post_bid()).toBe(undefined);
      expect(scope.alerts.length).toBe(0);
  });

  it('should show validation again after cancelling', function () {
      scope.form.BidsForm.bid.$setViewValue('700');
      scope.$digest();
      expect(scope.form.bid).toEqual("700");

      // first try (error expected)
      expect(scope.force_post_low_bid).toBe(undefined);
      expect(scope.post_bid()).toBe(0);
      expect(scope.alerts[0].msg).toBe("You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?");

      // cancelling
      expect(scope.force_post_low_bid).toBe(700);
      expect(scope.post_bid(-1)).toBe(undefined);
      expect(scope.alerts.length).toBe(0);

      // again first try (error expected)
      expect(scope.post_bid()).toBe(0);
      expect(scope.alerts[0].msg).toBe("You are going to decrease your bid by {{too_low_bid_ratio}}%. Are you sure?");

      // second click
      expect(scope.post_bid()).toBe(undefined);
      expect(scope.alerts.length).toBe(0);
  });

});