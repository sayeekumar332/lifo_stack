import os
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb_test.simulator import run


@cocotb.test()
async def example_test(dut):
    pass


def test_lifo_stack_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [str(proj_path / "sources/lifo_stack.v")]

    run(
        verilog_sources=sources,
        toplevel="lifo_stack",
        module="test_lifo_stack_hidden",  # cocotb test module name
        sim=sim,
    )

