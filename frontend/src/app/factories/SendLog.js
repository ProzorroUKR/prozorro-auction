angular.module('auction').factory('sendLog', ['$http', function($http) {
    return function(msg, level, context) {
        var context = context || {};
        // update global context
        if(angular.isObject(msg) && !angular.isArray(msg)){
            angular.forEach(msg, function(value, key) {
                context[key.toUpperCase()] = value;
            });
        }
        // it's important to make a copy, cos the global object may be changed before request is sent
        var entry = angular.copy(context);
        entry["LEVEL"] = level;
        entry["BROWSER_CLIENT_TIMESTAMP"] = (new Date()).toISOString();

        // getting message
        if(angular.isString(msg)){
            entry["MESSAGE"] = msg;
        }else if(angular.isObject(msg) && angular.isDefined(msg.message)){
            entry["MESSAGE"] = msg.message;
        }else{
            entry["MESSAGE"] = msg.toString();
        }
        // getting error stack trace
        if(angular.isObject(msg)){
          if(angular.isDefined(msg.stack)){
            entry["STACK"] = msg.stack;
          }
        }
        $http.post('/api/log', entry).catch(function (err) {console.error(err)});
    };
}]);