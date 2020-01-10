angular.module('auction').directive('format', ['$filter', function ($filter) {
    return {
        require: '?ngModel',
        link: function (scope, elem, attrs, ctrl) {
            if (!ctrl) {
                return;
            }

            ctrl.$formatters.unshift(function () {
                // this func is called when value is loaded from model
                return $filter('floor')(ctrl.$modelValue, 2);
            });

            ctrl.$parsers.unshift(function (viewValue) {
                // this func is called when value is loaded from input
                var plainNumber = viewValue.replace(/[^\d\,\.]/g, '');

                if(plainNumber.indexOf(".") !== -1){
                    // for inputs like 1,000.55 (in case Ctr+V)
                    plainNumber = plainNumber.replace(/[\,]/g, '');
                }else{
                    // for inputs like 1000,55
                    plainNumber = plainNumber.replace(/[\,]/g, '.');
                }
                // handle multiple decimal dots(comas): 1.000.55 => 1000.55
                plainNumber = plainNumber.replace(/\.(?=.*\.)/, '');

                // plainNumber format is 20000.02
                // formattedNumber format is 20 000,02
                var formattedNumber = $filter('floor')(plainNumber);  // 20 000
                var parts = plainNumber.split("."); // ,02
                if(parts.length > 1){
                    var float_part = parts[1].slice(0, 2);
                    formattedNumber = formattedNumber + "," + float_part;
                    plainNumber = parts[0] + "." + float_part;
                }
                elem.val(formattedNumber);
                return plainNumber;
            });
        }
    };
}]);