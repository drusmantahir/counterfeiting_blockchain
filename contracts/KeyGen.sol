// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract KeyGen {
    struct Key {
        string key;
        bool consumed;
    }

    mapping(string => Key) private keys;
    address private owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addKey(string memory _key) public onlyOwner {
        require(bytes(_key).length > 0, "Key cannot be empty");
        require(!keys[_key].consumed, "Key already exists and is consumed");

        keys[_key] = Key(_key, false);
    }

    function consumeKey(string memory _key) public onlyOwner {
        require(bytes(_key).length > 0, "Key cannot be empty");
        require(!keys[_key].consumed, "Key is already consumed or does not exist");

        keys[_key].consumed = true;
    }

    function isKeyConsumed(string memory _key) public view returns (bool) {
        return keys[_key].consumed;
    }

    function getOwner() public view returns (address) {
        return owner;
    }
}

