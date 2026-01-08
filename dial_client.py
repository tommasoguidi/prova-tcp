import time
import base64
from unaiverse.networking.p2p import P2P
from unaiverse.networking.p2p.messages import Msg


def run_client():
    P2P.setup_library(enable_logging=True)
    node_config = {
            "identity_dir": "./id_client",
            "port": 0,
            "ips": None,
            "enable_relay_client": False,
            "enable_relay_service": False,
            "knows_is_public": False,
            "enable_tls": False,
            "domain_name": None,
            "tls_cert_path": None,
            "tls_key_path": None,
            "dht_enabled": False,
            "dht_mode": 'client',
            "dht_keep": False
        }
    node = P2P(**node_config)
    print(f"Client avviato. ID: {node.peer_id}")

    target_addr = '/ip4/193.205.7.181/tcp/20200/p2p/12D3KooWMaiQN4ZXsFkHRex4gsn64m5fhgEMShbPpnYZ3UtFUV9J'
    try:
        info = node.connect_to([target_addr])
        target_id = info['ID']
        print(f"Connesso a {target_id}!")
    except Exception as e:
        print(f"Connessione fallita: {e}")
        return

    print("Scrivi un messaggio e premi invio. CTRL+C per uscire.")
    
    # Canale per inviare a Target
    channel_out = f"{node.peer_id}::dm:{target_id}"

    while True:
        try:
            text_input = input(f"Tu -> {target_id[:5]}: ")
            if not text_input: continue

            # 1. Creazione oggetto Msg
            msg_out = Msg(
                sender=node.peer_id,
                content=text_input,      # La classe Msg gestirà questo come json_content
                channel=channel_out,
                content_type=Msg.MISC
            )

            # 2. Invio serializzato
            node.send_message_to_peer(channel_out, msg_out.to_bytes())

            # 3. Loop di attesa risposta
            print(" ... attendo risposta ...")
            got_reply = False
            for _ in range(50): 
                raw_msgs = node.pop_messages()
                for raw_m in raw_msgs:
                    base64_data = raw_m.get("data")
                    decoded_data = base64.b64decode(base64_data)
                    reply_obj = Msg.from_bytes(decoded_data)
                    print(f"[{reply_obj.sender[:5]}]: {reply_obj.content}")
                    got_reply = True
                
                if got_reply: break
                time.sleep(0.1)
            
            if not got_reply:
                print("(Nessuna risposta ricevuta)")

        except KeyboardInterrupt:
            print("\nBye.")
            node.close()
            break

if __name__ == "__main__":
    run_client()
