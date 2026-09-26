import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat({
	baseDirectory: dirname(fileURLToPath(import.meta.url)),
});

const config = [
	{ ignores: ['.next/**'] },
	...compat.extends('next/core-web-vitals'),
	{
		rules: {
			'@next/next/no-html-link-for-pages': 'off',
			'react/no-unescaped-entities': 'off',
		},
	},
];

export default config;
