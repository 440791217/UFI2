dst_regs = ['ip', 'r0', 'ip', 'r1']
dst_regs = ['r12' if reg == 'ip' else reg for reg in dst_regs]
print(dst_regs)
    