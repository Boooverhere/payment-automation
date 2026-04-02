#!/bin/bash
curl -s -X POST https://pay.iptvsup.com/webhook/email-click \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer aea394b7dc25b6dea1f0fc7a72c5fac49da7ae38f174607b7b8009577e79185a" \
  -d '{"event":"click","email":"test@example.com","link":"https://www.iptvsup.com/checkout/?add-to-cart=2711"}'
