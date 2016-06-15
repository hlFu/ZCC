	.intel_syntax noprefix
	.local ss
	.comm ss,4,4
	.comm g_i,4,4
	.local sss
	.comm sss,4,4
	.section .rodata
	.text
	.globl main
	.type main, @function
main:
	push ebp
	mov ebp, esp
	sub esp, 32
	add eax, 1
	mov edx, 2
	sub eax, edx
	mov edi, 3
	mov esi, 4
	mov [esp+16], eax
	call foo
	leave
	ret
	.size main, .-main
	.globl foo
	.type foo, @function
foo:
	push ebp
	mov ebp, esp
	push edi
	sub esp, 32
	mov eax, 2
	mov edi, 3
	add eax, 1
	pop edi
	leave
	ret
	.size foo, .-foo
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
