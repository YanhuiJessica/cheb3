pragma solidity ^0.8.20;

contract VulnWETH {
    string constant public name     = "Vulnerable Wrapped Ether";
    string constant public symbol   = "VulnWETH";
    uint8  constant public decimals = 18;

    mapping (address => uint)                       public  balanceOf;
    mapping (address => mapping (address => uint))  public  allowance;

    fallback() external payable {
        deposit();
    }

    receive() external payable {
        deposit();
    }

    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
    }

    function withdraw(uint wad) public {
        require(balanceOf[msg.sender] >= wad);
        payable(msg.sender).call{value: wad, gas: 7000}("");
        unchecked {
            balanceOf[msg.sender] -= wad;
        }
    }

    function totalSupply() public view returns (uint) {
        return address(this).balance;
    }

    function approve(address guy, uint wad) public returns (bool) {
        allowance[msg.sender][guy] = wad;
        return true;
    }

    function transfer(address dst, uint wad) public returns (bool) {
        uint256 rbalance = balanceOf[msg.sender];
        require(rbalance >= wad);

        unchecked {
            balanceOf[msg.sender] = rbalance - wad;
            balanceOf[dst] += wad;
        }
        return true;
    }

    function transferFrom(address src, address dst, uint wad)
        public
        returns (bool)
    {
        require(balanceOf[src] >= wad);

        if (src != msg.sender && allowance[src][msg.sender] != type(uint).max) {
            require(allowance[src][msg.sender] >= wad);
            allowance[src][msg.sender] -= wad;
        }

        balanceOf[src] -= wad;
        balanceOf[dst] += wad;

        return true;
    }
}