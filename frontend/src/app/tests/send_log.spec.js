describe('sendLog', function() {
  var $httpBackend, sendLog;

  beforeEach(module('auction'));
  beforeEach(inject(function(_$httpBackend_, _sendLog_) {
     $httpBackend = _$httpBackend_;
     sendLog = _sendLog_;
  }));

  it('should send log', function() {
    $httpBackend.expectPOST(
        '/log',
        function(data) {
            data = JSON.parse(data);
            expect(data["MESSAGE"]).toBe("Hello, world!");
            expect(data["LEVEL"]).toBe("INFO");
            expect(data["ADDITIONALLY"]).toBe("Bye!");
            expect(data["BROWSER_CLIENT_TIMESTAMP"]).toBeDefined();
            return true
         }
    ).respond(200);
    sendLog("Hello, world!", "INFO", {"ADDITIONALLY": "Bye!"});
    expect($httpBackend.flush).not.toThrow();
  });

  it('should send log from exception', function() {
    var error = new Error("Unexpected something");
    error.stack = "...";
    $httpBackend.expectPOST(
        '/log',
        function(data) {
            data = JSON.parse(data);
            expect(data["MESSAGE"]).toBe("Unexpected something");
            expect(data["STACK"]).toBe("...");
            expect(data["LEVEL"]).toBe("ERROR");
            expect(data["BROWSER_CLIENT_TIMESTAMP"]).toBeDefined();
            return true
         }
    ).respond(200);
    sendLog(error, "ERROR");
    expect($httpBackend.flush).not.toThrow();
  });

  it('should send log object', function() {
    $httpBackend.expectPOST(
        '/log',
        function(data) {
            data = JSON.parse(data);
            expect(data["MESSAGE"]).toBe("Hi");
            expect(data["ADD"]).toBe("THIS");
            expect(data["LEVEL"]).toBe("INFO");
            expect(data["BROWSER_CLIENT_TIMESTAMP"]).toBeDefined();
            return true
         }
    ).respond(200);
    sendLog({"message": "Hi", "ADD": "THIS"}, "INFO");
    expect($httpBackend.flush).not.toThrow();
  });

  it('should send log object to string', function() {
    $httpBackend.expectPOST(
        '/log',
        function(data) {
            data = JSON.parse(data);
            expect(data["MESSAGE"]).toBe("1,2");
            expect(data["LEVEL"]).toBe("INFO");
            expect(data["BROWSER_CLIENT_TIMESTAMP"]).toBeDefined();
            return true
         }
    ).respond(200);
    sendLog([1, 2], "INFO");
    expect($httpBackend.flush).not.toThrow();
  });

  afterEach(function() {
     $httpBackend.verifyNoOutstandingExpectation();
     $httpBackend.verifyNoOutstandingRequest();
  });

});
