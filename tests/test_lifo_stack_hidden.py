import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


# ================================================================
#  TESTCASE 1 : RESET OPERATION
# ================================================================
@cocotb.test()
async def test_reset_operation(dut):
    """Test Case 1: Reset Operation"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize inputs
    dut.stack_reset.value = 0
    dut.stack_push.value = 0
    dut.stack_pop.value = 0
    dut.stack_we.value = 0
    dut.stack_re.value = 0
    dut.stack_mux_sel.value = 0
    dut.stack_data_1_in.value = 0
    dut.stack_data_2_in.value = 0

    # Let clock stabilize
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Apply reset
    dut.stack_reset.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.stack_reset.value = 0  # deassert reset

    await RisingEdge(dut.clk)

    # Checks
    assert dut.empty_o.value == 1, "After reset, empty_o must be 1"
    assert dut.full_o.value == 0,  "After reset, full_o must be 0"
    assert dut.stack_data_out.value == 0, "Data_out must be 0 when stack_re=0"

    dut._log.info("Reset operation test PASSED.")


# ================================================================
#  TESTCASE 2 : PUSH OPERATION
# ================================================================
@cocotb.test()
async def test_push_operation(dut):
    """Test Case 2: Push Operation"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # INITIALIZE
    dut.stack_reset.value = 1
    dut.stack_push.value = 0
    dut.stack_pop.value = 0
    dut.stack_we.value = 0
    dut.stack_re.value = 0
    dut.stack_mux_sel.value = 1   # select stack_data_1_in
    dut.stack_data_1_in.value = 0
    dut.stack_data_2_in.value = 0

    # Apply reset for 2 cycles
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.stack_reset.value = 0

    await RisingEdge(dut.clk)

    # =====================================================
    # STEP 1 : Write data into RAM at current pointer
    # =====================================================
    dut.stack_data_1_in.value = 0xA   # push value
    dut.stack_we.value = 1            # write enable

    await RisingEdge(dut.clk)         # perform write
    dut.stack_we.value = 0

    # =====================================================
    # STEP 2 : Increment stack pointer using PUSH
    # =====================================================
    dut.stack_push.value = 1
    await RisingEdge(dut.clk)
    dut.stack_push.value = 0

    await RisingEdge(dut.clk)

    # Pointer must be non-zero → not empty
    assert dut.empty_o.value == 0, "Stack must NOT be empty after one push"

    # Stack should not be full
    assert dut.full_o.value == 0, "Stack should NOT be full after one push"

    assert dut.stack_addr_w.value == 1, "Stack address should be incremented after a push operation"

    assert dut.stack_data_in_w.value == 0xA, "Invalid data given"
    dut._log.info("Push operation test PASSED.")

# ================================================================
#  TESTCASE 3 : POP OPERATION (NO RESET IN THIS TEST)
# ================================================================
@cocotb.test()
async def test_pop_operation(dut):
    """Test Case 3: Pop Operation (Assumes previous push has occurred)"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # -------------------------------------------------------
    # DO NOT RESET HERE — assume previous test already pushed
    # -------------------------------------------------------

    dut.stack_push.value = 0
    dut.stack_pop.value = 0
    dut.stack_we.value = 0
    dut.stack_re.value = 0

    await RisingEdge(dut.clk)

    # -------------------------------------------------------
    # CHECK INITIAL STATE BEFORE POP
    # -------------------------------------------------------
    dut._log.info(f"Initial stack_addr_w = {int(dut.stack_addr_w.value)}")

    assert dut.stack_addr_w.value == 1, \
        "Stack pointer must be 1 before pop (one push should have occurred)"

    assert dut.empty_o.value == 0, \
        "Stack must NOT be empty before pop"

    # -------------------------------------------------------
    # PERFORM POP OPERATION
    # -------------------------------------------------------
    dut.stack_pop.value = 1
    await RisingEdge(dut.clk)
    dut.stack_pop.value = 0

    await RisingEdge(dut.clk)

    # -------------------------------------------------------
    # VALIDATE POST-POP STATE
    # -------------------------------------------------------
    dut._log.info(f"After POP stack_addr_w = {int(dut.stack_addr_w.value)}")
    
    dut.stack_re.value = 1
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    dut.stack_re.value = 0

    # Pointer must decrement
    assert dut.stack_addr_w.value == 0, \
        "Stack pointer should decrement to 0 after pop"

    # Stack must now be empty
    assert dut.empty_o.value == 1, \
        "Stack must be EMPTY after popping the last entry"

    # Full must be low
    assert dut.full_o.value == 0, \
        "Stack must NOT be full after pop"
        
    assert dut.stack_data_out.value == 0xA, "Invalid data fetched"    

    dut._log.info("Pop operation test PASSED.")

# ================================================================
#  TESTCASE 4 : FULL FLAG TEST
# ================================================================
@cocotb.test()
async def test_full_flag(dut):
    """Test Case 4: FULL FLAG test"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # ---- Assume previous tests left stack EMPTY (stack_addr = 0) ----
    # ---- We do NOT reset here ----
    dut.stack_push.value = 0
    dut.stack_pop.value = 0
    dut.stack_re.value = 0
    dut.stack_we.value = 0
    dut.stack_mux_sel.value = 1    # choose stack_data_1_in

    await RisingEdge(dut.clk)

    dut._log.info(f"Initial SP = {int(dut.stack_addr_w.value)}")

    # Stack must be empty before starting
    assert dut.stack_addr_w.value == 0, \
        "Stack pointer must be 0 before FULL test"

    # ===========================================================
    # Fill stack from address 0 to 16
    # ===========================================================
    for i in range(17):   # 0 .. 16 inclusive
        dut.stack_data_1_in.value = i & 0xF   # write some pattern
        dut.stack_we.value = 1                # write first
        await RisingEdge(dut.clk)
        dut.stack_we.value = 0

        dut.stack_push.value = 1              # then push pointer
        await RisingEdge(dut.clk)
        dut.stack_push.value = 0

        await RisingEdge(dut.clk)

        dut._log.info(f"PUSH #{i}: SP = {int(dut.stack_addr_w.value)}")

    # ===========================================================
    # Check FULL condition
    # ===========================================================
    assert dut.stack_addr_w.value == 16, \
        "Stack pointer must be 16 when FULL"

    assert dut.full_o.value == 1, \
        "FULL flag must be 1 when stack pointer reaches 16"

    assert dut.empty_o.value == 0, \
        "EMPTY must be 0 when stack is full"

    # ===========================================================
    # Try one more push → pointer MUST NOT increment
    # ===========================================================
    prev_sp = int(dut.stack_addr_w.value)

    dut.stack_data_1_in.value = 0xF
    dut.stack_we.value = 1
    await RisingEdge(dut.clk)
    dut.stack_we.value = 0

    dut.stack_push.value = 1
    await RisingEdge(dut.clk)
    dut.stack_push.value = 0

    await RisingEdge(dut.clk)

    new_sp = int(dut.stack_addr_w.value)
    dut._log.info(f"SP after extra push attempt = {new_sp}")

    assert new_sp == prev_sp, \
        "SP must NOT increment when FULL"

    dut._log.info("FULL FLAG test PASSED.")

# ================================================================
#  TESTCASE 5 : EMPTY FLAG TEST (SELF-CONTAINED)
# ================================================================
@cocotb.test()
async def test_empty_flag(dut):
    """Test Case 5: EMPTY FLAG test"""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Initialize
    dut.stack_push.value = 0
    dut.stack_pop.value = 0
    dut.stack_we.value = 0
    dut.stack_re.value = 0
    dut.stack_mux_sel.value = 1

    await RisingEdge(dut.clk)

    # ==========================================================
    # 1. Fill stack (0 → 16)
    # ==========================================================
    for i in range(17):   # 0..16 inclusive
        dut.stack_data_1_in.value = i & 0xF
        dut.stack_we.value = 1
        await RisingEdge(dut.clk)
        dut.stack_we.value = 0

        dut.stack_push.value = 1
        await RisingEdge(dut.clk)
        dut.stack_push.value = 0

        await RisingEdge(dut.clk)

    # Confirm FULL
    assert dut.stack_addr_w.value == 16
    assert dut.full_o.value == 1
    assert dut.empty_o.value == 0

    dut._log.info("Stack filled to FULL. Starting EMPTY test...")

    # ==========================================================
    # 2. POP from 16 → 0
    # ==========================================================
    for sp in range(16, -1, -1):

        # READ FIRST (your RTL style)
        dut.stack_re.value = 1
        await RisingEdge(dut.clk)
        read_data = int(dut.stack_data_out.value)
        dut.stack_re.value = 0

        dut._log.info(f"Read @ SP={sp} → data={read_data}")

        # POP NEXT (your RTL style)
        dut.stack_pop.value = 1
        await RisingEdge(dut.clk)
        dut.stack_pop.value = 0

        await RisingEdge(dut.clk)

        dut._log.info(f"After POP: SP = {int(dut.stack_addr_w.value)}")

    # ==========================================================
    # 3. Final empty checks
    # ==========================================================
    assert dut.stack_addr_w.value == 0, "SP must be 0 when EMPTY"
    assert dut.empty_o.value == 1, "EMPTY flag must be 1"
    assert dut.full_o.value == 0, "FULL must be 0 when EMPTY"

    dut._log.info("EMPTY FLAG test PASSED.")

# ⚠️ CRITICAL: Every test needs this pytest wrapper
def test_lifo_stack_hidden_runner():
    import os
    from pathlib import Path
    from cocotb_tools.runner import get_runner
    
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    sources = [proj_path / "sources/lifo_stack.v"]  # Note: sources/ not rtl/
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="lifo_stack",
        always=True,
    )
    runner.test(
        hdl_toplevel="lifo_stack",
        test_module="test_lifo_stack_hidden"
    )





