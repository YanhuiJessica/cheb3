// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.18;

import {HighSecurityGate} from "./FortifiedPerimeter.sol";

contract Setup {
    HighSecurityGate public immutable TARGET;

    constructor() {
        TARGET = new HighSecurityGate();
    }

    function isSolved() public view returns (bool) {
        return TARGET.strcmp(TARGET.lastEntrant(), "Pandora");
    }
}
