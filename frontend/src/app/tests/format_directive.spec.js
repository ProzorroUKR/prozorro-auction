describe('Post Bid Form Tests', function () {
    var controller, scope, rootScope, input_element;
    beforeEach(module('auction'));
    beforeEach(inject(function($compile, $rootScope) {
        rootScope = $rootScope;
        rootScope.input_model = "";
        var element = angular.element(
          '<for><input ng-model="input_model" format></form>'
        );
        input_element = element.find('input');
        $compile(input_element)(rootScope);
    }));
    function set_input_value(value){
        input_element.val(value)[0].dispatchEvent(new Event('input'));
        rootScope.$digest();
    }
    it('formatting test', function () {
        set_input_value("1000000.54921");

        expect(input_element.val()).toEqual("1 000 000,54");
        expect(rootScope.input_model).toEqual("1000000.54");
    });
    it('formatting comas and dot', function () {
        set_input_value("1,000,000.5");

        expect(input_element.val()).toEqual("1 000 000,5");
        expect(rootScope.input_model).toEqual("1000000.5");
    });
    it('formatting spaces and dot', function () {
        set_input_value("1 000 000.5");

        expect(input_element.val()).toEqual("1 000 000,5");
        expect(rootScope.input_model).toEqual("1000000.5");
    });
    it('formatting spaces and comma', function () {
        set_input_value("1 000 000,5");

        expect(input_element.val()).toEqual("1 000 000,5");
        expect(rootScope.input_model).toEqual("1000000.5");
    });
    it('handle multiple dots', function () {
        set_input_value("1000,000,5");

        expect(input_element.val()).toEqual("1 000 000,5");
        expect(rootScope.input_model).toEqual("1000000.5");
    });
    it('set value from model', function () {
        rootScope.input_model = "1000000.54";
        rootScope.$digest();
        expect(input_element.val()).toEqual("1 000 000,54");
    });
});