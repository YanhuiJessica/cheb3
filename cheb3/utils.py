
def compile_file(contract_file: str,
                 contract_names: str | list[str] = None,
                 solc_version: str = None,
                 base_path: str = None
                 ) -> dict[tuple[dict, str]]:
    return compile_sol(open(contract_file, 'r', encoding="utf-8").read(),
                       contract_names=contract_names,
                       solc_version=solc_version,
                       base_path=base_path)


def compile_sol(contract_source: str,
                contract_names: str | list[str] = None,
                solc_version: str = None,
                base_path: str = None
                ) -> dict[tuple[dict, str]]:
    r"""
    Compile the Solidity source and return the ABI and bytecode of
    the specific contracts.

    Arguments:
        contract_source (str): The Solidity source code.
        contract_name (str | list[str]): A target contract name or
            a list of target contract names. If not given, it will
            return all contracts in the source file.
        solc_version (str): `solc` version to use. If not given, the
            currently active version is used. If the specified version
            is not installed, it will be installed automatically.
        base_path (str): Use the given path as the root of the source
            tree to include other dependence contracts, e.g. the path to
            openzeppelin contracts.

    Returns:
        A dict, mapping the contract name to a tuple of the ABI and bytecode.
    """

    from solcx import compile_source, set_solc_version
    from solcx.exceptions import SolcNotInstalled

    try:
        set_solc_version(solc_version)
    except SolcNotInstalled:
        from solcx.install import install_solc
        install_solc(solc_version)
        set_solc_version(solc_version)

    compiled = compile_source(contract_source,
                              output_values=["abi", "bin"],
                              solc_version=solc_version,
                              base_path=base_path)
    contracts = dict()
    if contract_names is None:
        contract_names = [c.split(':')[1] for c in compiled.keys() if c.startswith('<stdin>:')]
    if isinstance(contract_names, str):
        contract_names = [contract_names]
    for cn in contract_names:
        if f'<stdin>:{cn}' not in compiled:
            raise Exception(f"Contract {cn} not found.")
        contracts[cn] = (compiled[f'<stdin>:{cn}']['abi'], compiled[f'<stdin>:{cn}']['bin'])
    return contracts
