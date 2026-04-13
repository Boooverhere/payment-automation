<?php
define( 'CHECKOUT_CAPTURE_SECRET', 'iptvsup-abandoned-2026' );
/**
 * Abandoned Checkout Capture
 * ----------------------------
 * When a visitor fills in their billing email on the checkout page,
 * this fires a beacon to /webhook/checkout-started so the abandoned
 * checker can follow up after 2 hours if no order is placed.
 *
 * Installation: paste into WooCommerce > Settings > Advanced > Custom code,
 * or add to wp-content/mu-plugins/abandoned-checkout-capture.php
 */

add_action( 'woocommerce_after_checkout_billing_form', function() {
    if ( ! WC()->cart || WC()->cart->is_empty() ) return;

    // Build the add-to-cart URL from the first cart item
    $cart_items  = WC()->cart->get_cart();
    $first_item  = reset( $cart_items );
    $product_id  = $first_item ? (int) $first_item['product_id'] : 0;
    $checkout_url = $product_id
        ? 'https://www.iptvsup.com/checkout/?add-to-cart=' . $product_id
        : 'https://www.iptvsup.com/checkout/';

    $webhook_url = 'https://pay.iptvsup.com/webhook/checkout-started?token=' . CHECKOUT_CAPTURE_SECRET;

    ?>
    <script>
    (function () {
        var webhookUrl  = <?php echo json_encode( $webhook_url ); ?>;
        var checkoutUrl = <?php echo json_encode( $checkout_url ); ?>;
        var fired = false;

        function sendCapture( email ) {
            if ( fired ) return;
            if ( ! email || email.indexOf('@') === -1 ) return;
            fired = true;

            var payload = JSON.stringify({ email: email, checkout_url: checkoutUrl });

            // sendBeacon is fire-and-forget — works even on page unload
            if ( navigator.sendBeacon ) {
                navigator.sendBeacon( webhookUrl, new Blob( [payload], { type: 'application/json' } ) );
            } else {
                // Fallback for older browsers
                var xhr = new XMLHttpRequest();
                xhr.open( 'POST', webhookUrl, false ); // sync so it runs before unload
                xhr.setRequestHeader( 'Content-Type', 'application/json' );
                xhr.send( payload );
            }
        }

        document.addEventListener( 'DOMContentLoaded', function () {
            var emailField = document.getElementById( 'billing_email' );
            if ( ! emailField ) return;

            // Capture when user leaves the email field
            emailField.addEventListener( 'blur', function () {
                sendCapture( emailField.value.trim() );
            } );

            // Capture on page close/navigation as a safety net
            window.addEventListener( 'beforeunload', function () {
                sendCapture( emailField.value.trim() );
            } );
        } );
    })();
    </script>
    <?php
} );
