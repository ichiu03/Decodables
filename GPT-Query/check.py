story = """"
Once upon a time, in a lush and vibrant space, the Froglympics began. The pond gleamed in a brilliant hue, as insects zipped and shimmered, like diamonds in the light. Excitement filled the air as frogs of all sizes practiced their events. At the edge of the pond, Freddy the Frog peered, gazing at his reflection. His skin glistened in the light, but there was something about Freddy. He often tripped over his own feet, miscalculating his jumps. Yet, deep down, he wanted to compete in the Froglympics.

“Look at me, everyone! I’m here to take on the leap!” he said, puffing out his chest. But the others merely chuckled. “Good luck, Freddy! You’ll be great entertainment!” they croaked. Freddy’s spirits sank. Doubts crept in, telling him that maybe they were right. Just then, Tilly the Toad, his best friend, hopped over. Her tiny, kind face made Freddy feel better. “Don’t doubt yourself, Freddy! You need to trust in you. Let’s practice together!”

“But what if I mess up?” he asked, glancing down at the water. “Failure is just a stepping stone to success!” Tilly nudged him. “I’ll be there, and we can cheer each other on.” With Tilly by his side, they began their task, ready to face the challenges ahead and bring their goals to life, one leap at a time.Freddy and Tilly’s adventure began early the next morning. The sun peeked, casting a glow. “Let’s start the leap!” Tilly exclaimed, her face sparkling with enthusiasm. The pair hopped onto a lilypad, which swayed under their load. Freddy took a deep breath, ready to leap. He bent, aiming as best as he could. “Here goes nothing!” he cried. He leaped and landed in the mud, splatting everywhere! Tilly erupted in her croak, echoing. “Looks like you’re in the mud!” she chuckled, helping him out. “Maybe this isn’t meant for me,” Freddy mumbled, taking off the gooey mud. But Tilly tapped him gently. “Remember, we’re here to have fun!” They practiced jumps and croaking tunes, each session filled with giggles and flops. Tilly tumbled off her feet, gracefully gliding, while Freddy made his leap, a mix of grace and flair. Time flew by, with practice sessions and some mishaps, including the time Tilly slipped on a dew-covered rock and tumbled onto a pile of leaves. “You’ve got to admit, this is fun!” Tilly said, her sides aching from giggling. Finally, the day of the event arrived! The stage was a mix of color and delight, with competitors gathering, some in neat sports gear. Freddy’s heart raced as he met his fellow mates, performing in a dazzling display of skill. Cheers erupted in excitement, creating a symphony of enthusiasm. But as he looked around, Freddy couldn’t shake the bubbling doubts within him. Would he be able to do it? Would clumsiness ruin his dreams?Freddy glanced at Tilly, hopping up. "Freddy," she said, noticing his frown. "You a little!" "I don't," he replied. "They’re so." "If I mess up?" He looked left with each leap. Tilly hopped to him, her eyes sparkling with encouragement. “You’ve worked hard, and it’s not just about that. It’s about telling everyone your style!” She jiggled her nubby toes and gave him an encouraging nudge. “Just be you!” He lined up, taking in the medals and cheering. It was his time; he took a deep breath, remembering all the fun they had. “Yes, you can do this!” Tilly cheered from the sidelines, her voice echoing in the vibrant crowd. Freddy jogged to the edge of the deck, gathering himself and the joy he found in training. He bounded off the edge and into the air! He didn’t just jump – he twisted in mid-air and landed! The crowd erupted in cheers, not for the distance, but for the creativity he displayed. Freddy felt a smile spread across his face. He wasn’t a frog.

"""

sentences = story.split(".")
problems = 'w,qu,sh,or,oy,ar,igh'
problems = problems.split(",")
bad = 0
for sentence in sentences:
    for problem in problems:
        if problem in sentence:
            bad +=1
            break

n = len(sentences)
print(f'bad: {bad}, good: {n-bad}, total: {n}')
print((n-bad)/n)