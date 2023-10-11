def split_tex(text):
    """
    Takes a summary and splits it in a way that only the latex parts will be included with the NoEscape command

    :param doc:
    :param text:
    :return:
    """
    current_interval = ""
    dollar_count = 0
    total_dollar_count = text.count("$")
    print(total_dollar_count)

    for i, char in enumerate(text):
        if char == '$':
            dollar_count += 1
            if dollar_count % 2 == 1:  # One occurrence of '$': append interval up to $, set to zero again and add $
                print(current_interval)
                current_interval = "$"
            else:
                current_interval += "$"
                if i < len(text):
                    if text[i+1] == " ":
                        current_interval += " "
                print(current_interval)
                print(len(current_interval))
                current_interval = ""
        else:
            current_interval += char
    print(current_interval)


if __name__ == '__main__':
    sample = r"### Ion Trapping 1. Can we confine a particle with a static electric field? 2. What can we do about it? 3. Explain how the Paul trap works. 4. When does the pseudopotential approximation hold? 5. Explain stability with the appropriate diagram. 6. What textbook system can we use do describe our trapped particle? (QHO) 7. How does it look like for 2 ions? (normal modes) 8. Describe decoherence mechanisms for the system (dephasing, heating) ### Spin motion coupling 9. Let's talk about spin motion coupling. (free to lead from here, I started from the trapped ion interaction Hamiltonian in the z direction and did the Lamb Dicke Expansion) 10. In the atom field interaction, what is the field? (laser controlled by us) 11. What is $z_{0}$? (ground state wave packet size) 12. Why can we expand $e^{ik_{z}Z}$? ($\eta$ small, which we can see from typical laser wavelengths and ground state wave packet sizes) 13. What does this give to us now? (sidebands) 14. We have all the Hamiltonians now, but none of them include frequency. How do we get the sideband frequencies? (switch to interaction picture) ### Laser cooling 15. How does cooling with the red sideband work? 16. Can we just use the carrier and red sideband to drive the cooling process? Why do we need a dissipative (non-unitary) process? ### State dependent forces 17. How can we use the sidebands to implement state dependent forces? 18. Where does the state dependency come from?"
    split_tex(sample)
