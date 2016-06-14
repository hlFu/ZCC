	.file	"test9.c"
	.intel_syntax noprefix
	.globl	a
	.data
	.align 8
	.type	a, @object
	.size	a, 8
a:
	.long	0
	.long	1075052544
	.text
	.globl	foo
	.type	foo, @function
foo:
	push	ebp
	mov	ebp, esp
	sub	esp, 16
	mov	edx, DWORD PTR [ebp+8]
	mov	eax, DWORD PTR [ebp+16]
	mov	BYTE PTR [ebp-4], dl
	mov	WORD PTR [ebp-8], ax
	fld	QWORD PTR .LC0
	fstp	QWORD PTR [ebp+32]
	mov	WORD PTR [ebp+28], 2
	cmp	BYTE PTR [ebp-4], 97
	jne	.L2
	movsx	eax, WORD PTR [ebp-8]
	mov	edx, DWORD PTR [ebp+12]
	sub	edx, eax
	mov	eax, edx
	jmp	.L3
.L2:
	fld	QWORD PTR [ebp+32]
	movzx	eax, WORD PTR [ebp+28]
	mov	WORD PTR [ebp-6], ax
	fild	WORD PTR [ebp-6]
	fsubp	st(1), st
	fnstcw	WORD PTR [ebp-2]
	movzx	eax, WORD PTR [ebp-2]
	mov	ah, 12
	mov	WORD PTR [ebp-10], ax
	fldcw	WORD PTR [ebp-10]
	fistp	DWORD PTR [ebp-16]
	fldcw	WORD PTR [ebp-2]
	mov	eax, DWORD PTR [ebp-16]
.L3:
	leave
	ret
	.size	foo, .-foo
	.section	.rodata
.LC4:
	.string	"%lf"
.LC5:
	.string	"mamsf"
	.text
	.globl	main
	.type	main, @function
main:
	push	ebp
	mov	ebp, esp
	and	esp, -16
	sub	esp, 80
	fld	QWORD PTR .LC2
	fstp	QWORD PTR a
	mov	BYTE PTR [esp+60], 98
	mov	DWORD PTR [esp+64], 2
	mov	WORD PTR [esp+68], 3
	fld	QWORD PTR .LC3
	fstp	QWORD PTR [esp+72]
	fld	QWORD PTR [esp+72]
	fstp	QWORD PTR [esp+4]
	mov	DWORD PTR [esp], OFFSET FLAT:.LC4
	call	printf
	mov	DWORD PTR [esp+32], OFFSET FLAT:.LC5
	mov	eax, DWORD PTR [esp+60]
	mov	DWORD PTR [esp+12], eax
	mov	eax, DWORD PTR [esp+64]
	mov	DWORD PTR [esp+16], eax
	mov	eax, DWORD PTR [esp+68]
	mov	DWORD PTR [esp+20], eax
	mov	eax, DWORD PTR [esp+72]
	mov	DWORD PTR [esp+24], eax
	mov	eax, DWORD PTR [esp+76]
	mov	DWORD PTR [esp+28], eax
	mov	DWORD PTR [esp+8], 2
	mov	DWORD PTR [esp+4], 10
	mov	DWORD PTR [esp], 97
	call	foo
	leave
	ret
	.size	main, .-main
	.section	.rodata
	.align 8
.LC0:
	.long	0
	.long	1076166656
	.align 8
.LC2:
	.long	0
	.long	1074921472
	.align 8
.LC3:
	.long	-1717986918
	.long	1075157401
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
