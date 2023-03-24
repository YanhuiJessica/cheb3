pragma solidity ^0.8.18;


interface Entrant {
    function name() external returns (string memory);
}

contract HighSecurityGate {
    
    string[] private authorized = ["Orion", "Nova", "Eclipse"];
    string public lastEntrant;

    function enter() external {
        Entrant _entrant = Entrant(msg.sender);

        require(_isAuthorized(_entrant.name()), "Intruder detected");
        lastEntrant = _entrant.name();
    }

    function _isAuthorized(string memory _user) private view returns (bool){
        for (uint i; i < authorized.length; i++){
            if (strcmp(_user, authorized[i])){
                return true;
            }
        }
        return false;
    }

    function strcmp(string memory _str1, string memory _str2) public pure returns (bool){
        return keccak256(abi.encodePacked(_str1)) == keccak256(abi.encodePacked(_str2)); 
    }
}
