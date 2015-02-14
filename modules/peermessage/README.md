PeerMessage
===
Peermessage is a messaging app, similar in spirit to BitMessage or GPG-encrypted emails. However, it ties the sending of messages to the expenditure of a monetary currency (Peercoin), with the currency also providing the distribution mechanism for message meta data and access to other's gpg public keys. Only message meta data is stored in the blockchain, with the bulk of message data stored externally (more on that later).

## HOW DOES IT WORK?

### Starting up
 - Bob downloads a Peercoin wallet, and creates a Peercoin address (for example, 3BOBt1WpEZ73CNmQviecrnyiWrnqRhWNLy).
 - Bob funds his Peercoin address with a number of peercoins (for example, 5 ppc).
 - Bob download Peermessage.
 - Peermessage walks Bob through configuring his Peercoin wallet as a json-rpc server, which Peermessage will use to communicate to the network through.
 - Peermessage walks Bob through setting up GPG, and creating a set of GPG public/private keys for his Peercoin address (3BOBt1WpEZ73CNmQviecrnyiWrnqRhWNLy).
 - Every Peercoin address Bob has should have a different set of GPG keys associated with it - in this way, each address functions as a unique email inbox.

### Publishing your Public Key
 - Bob logs onto his Peermessage account with his Peercoin address 3BOBt1WpEZ73CNmQviecrnyiWrnqRhWNLy.
 - Peermessage tells Bob his public key for this address is not yet published on the network, which means he cannot yet receive encrypted messages.
 - Bob tells Peermessage to publish his public key.
 - Peermessage takes Bob's GPG public key, signs it with his Peercoin address, and appends the signature to it (result: public key + "|" + signature of public key) - the result of this is a string we'll call the payload.
 - Peermessage then takes the payload and hashes it, resulting in a unique payload key.
 - Peermessage contacts three external cloud stores - tinyurl.com, is.gd, and pastebin.com - and stores the payload under the payload key.
 - For an example of the above: tinyurl.com/<payload key> expands to random.com/<payload>
 - Peermessage then publishes an OP_RETURN transaction on the Peercoin blockchain, with the OP_RETURN message: "pmpka<payload key>", where "pm" stands for our app (Peermessage), "pka" stands for Public Key Announce, and the remaining bits are the payload key. This transaction comes from Bob's Peercoin address, and debits his account the standard Peercoin transaction fee (0.01 ppc).
 - Other clients see this transaction on the Peercoin blockchain originating from Bob's Peercoin address. They extract the payload key, download the payload from the external data store, and verify the signature attached to the payload with Bob's Peercoin address. If it matches, they store that GPG public key locally as attached to Bob's Peercoin address.

### Publishing a Message
 - Bob wants to send a message to Alice, who he knows owns the Peercoin address (3ALICEWpEZ73CNmQviecrnyiWrnqRhWNLy).
 - His Peermessage client has been constantly monitoring the blockchain, and saw that Alice published her public key (following the steps above) earlier. Peermessage verified her signature, and now has her GPG public key stored locally for Bob to use.
 - Bob write's a message to Alice, "Hi Alice!", and hits "Submit Message". Peermessage takes this message, encrypts it with Alice's GPG public key, signs the message with Bob's signature from his Peercoin address, and appends the signature to the string - resulting in a string we'll call the payload. The payload is hashed to create a payload key.

```
encrypted_message = GPG_encrypt("Hi Alice!", Alice_gpg_public_key)
signature = Peercoin.sign(encrypted_message, Bob_peercoin_address)
payload = encrypted_message + "|" + signature
payload_key = hash(payload)
```

 - Peermessage contacts three external cloud stores - tinyurl.com, is.gd, and pastebin.com - and stores the payload under the payload key.
 - For an example of the above: tinyurl.com/<payload key> expands to random.com/<payload>
 - Peermessage then publishes an OP_RETURN transaction on the Peercoin blockchain, with the OP_RETURN message: "pmmsg<payload key>", where "pm" stands for our app (Peermessage), "msg" stands for message, and the remaining bits are the payload key. This transaction comes from Bob's Peercoin address, and debits his account the standard Peercoin transaction fee (0.01 ppc).
 - Other clients see this transaction on the Peercoin blockchain originating from Bob's Peercoin address. They extract the payload key, download the payload from the external data store, and verify the signature attached to the payload with Bob's Peercoin address. If it matches, they then cycle through all their GPG private keys trying to decrypt the message. If they successfully decrypt it, they know it was sent to them, and Peermessage displays the plaintext message to the intended recipient.
