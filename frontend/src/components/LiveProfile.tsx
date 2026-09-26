'use client';
import {useEffect,useState} from 'react';import {api} from '../lib/api';
export function LiveProfile({field,fallback}:{field:string,fallback:string}){const [value,setValue]=useState(fallback);useEffect(()=>{api<any>('/public/profile').then(x=>setValue(x[field]||fallback)).catch(()=>{})},[field,fallback]);return <>{value}</>}
