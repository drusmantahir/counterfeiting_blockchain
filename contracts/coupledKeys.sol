// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CoupledKeys {
    struct Key {
        string key;
        string image; // Attribute to store the image URL or identifier
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

    function addKeysBatch(string[] memory _keys) public onlyOwner {
        for (uint i = 0; i < _keys.length; i++) {
            string memory key = _keys[i];
            require(bytes(key).length > 0, "Key cannot be empty");
            require(!keys[key].consumed, "Key already exists and is consumed");

            keys[key] = Key(key, false);
        }
    }

    function addKeyWithImage(string memory _key, string memory _image) public onlyOwner {
        require(bytes(_key).length > 0, "Key cannot be empty");
        require(bytes(_image).length > 0, "Image URL cannot be empty");
        require(!keys[_key].consumed, "Key already exists and is consumed");

        // Add the key with the image if it does not already exist
        if (bytes(keys[_key].key).length == 0) { // Check if key does not exist
            keys[_key] = Key(_key, _image, false);
        } else {
            revert("Key already exists");
        }
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

    function getImageAndStatus(string memory _key) public view returns (string memory image, bool consumed) {
        require(bytes(_key).length > 0, "Key cannot be empty");

        Key memory keyData = keys[_key];
        require(bytes(keyData.key).length > 0, "Key does not exist");

        return (keyData.image, keyData.consumed);
    }


    function getAllKeys() public view returns (string[] memory keysList, string[] memory imagesList, bool[] memory consumedList) {
        uint256 totalKeys = 0;

        // First, determine the number of keys
        for (uint i = 0; i < totalKeys; i++) {
            if (bytes(keys[keys[i]].key).length > 0) {
                totalKeys++;
            }
        }

        // Initialize arrays
        string[] memory tempKeysList = new string[](totalKeys);
        string[] memory tempImagesList = new string[](totalKeys);
        bool[] memory tempConsumedList = new bool[](totalKeys);

        uint256 index = 0;
        // Populate arrays with key data
        for (uint i = 0; i < totalKeys; i++) {
            Key memory keyData = keys[keys[i]];
            if (bytes(keyData.key).length > 0) {
                tempKeysList[index] = keyData.key;
                tempImagesList[index] = keyData.image;
                tempConsumedList[index] = keyData.consumed;
                index++;
            }
        }

        return (tempKeysList, tempImagesList, tempConsumedList);
    }
}
